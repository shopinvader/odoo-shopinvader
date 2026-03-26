# Copyright 2022 ACSONE SA/NV
# Copyright 2024 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict, namedtuple
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from odoo import api, fields
from odoo.exceptions import MissingError
from odoo.tools import float_compare

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale.models.sale_order_line import SaleOrderLine
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import CartSyncInput, CartTransaction, CartUpdateInput

cart_router = APIRouter(tags=["carts"])


class CartHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_cart.cart_router.helper"
    _description = "ShopInvader API Cart Router Helper"
    _model = "sale.order"

    partner = fields.Many2one("res.partner", required=True)

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
        ]

    def _get_cart(self, uuid: UUID | None):
        return self.env["sale.order"]._find_open_cart(
            self.partner.id, str(uuid) if uuid else None
        )

    def _get_transaction_key(self, transaction: CartTransaction):
        """
        Return a namedtuple of values that identify a transaction and match it
        against a cart line.

        To override this method create a new namedtuple combining the super fields
        and the new ones and return it with the values that identify the transaction.

        Example:
        ```python

        def _get_transaction_key(self, transaction: CartTransaction):
            key = super()._get_transaction_key(transaction)
            return namedtuple(
                key.__class__.__name__, key._fields + ('my_field',)
            )(
                *key,
                my_field=transaction.my_field,
            )
        ```

        """
        return namedtuple("TransactionKey", ["product_id"])(transaction.product_id)

    @api.model
    def _check_transactions(self, transactions: list[CartTransaction]):
        """Check if the transactions info are valid.

        This method car be extended to validate if the product_id is
        sellable via the rest api, or ...
        """
        for transaction in transactions:
            if not self.env["product.product"].browse(transaction.product_id).exists():
                raise MissingError(
                    self.env._(
                        f"Product with id {transaction.product_id} not existing."
                    )
                )

    @api.model
    def _group_transactions(self, transactions: list[CartTransaction]):
        """
        Gather together transactions that are linked to the same transaction key.
        """
        grouped_transactions = defaultdict(list)
        for transaction in transactions:
            key = self._get_transaction_key(transaction)
            grouped_transactions[key].append(transaction)
        return grouped_transactions

    @api.model
    def _apply_transactions_on_existing_cart_line(
        self, cart_line: SaleOrderLine, transactions: list[CartTransaction]
    ):
        """Apply transactions to current line and return a record write command
        to apply to the one2many field on SO.

        """
        cart_line.ensure_one()
        delta_qty = sum(t.qty for t in transactions)
        new_qty = cart_line.product_uom_qty + delta_qty
        if (
            float_compare(new_qty, 0, precision_rounding=cart_line.product_uom.rounding)
            <= 0
        ):
            return (2, cart_line.id, None)
        vals = {"product_uom_qty": new_qty}
        vals = self._apply_transactions_on_existing_cart_line_prepare_vals(
            cart_line, transactions, vals
        )
        return (1, cart_line.id, vals)

    @api.model
    def _apply_transactions_on_existing_cart_line_prepare_vals(
        self,
        line: SaleOrderLine,
        transactions: list[CartTransaction],
        values: dict,
    ):
        """Post hook allowing to add custom values in cart lines to be updated.

        Meant to be overridden
        """
        return values

    @api.model
    def _apply_transactions_creating_new_cart_line(
        self, cart: SaleOrder, transactions: list[CartTransaction]
    ):
        """Create a record create command to apply to the one2many field on SO
        from transactions.
        """
        vals = self._prepare_line_from_transactions(
            cart=cart, transactions=transactions
        )
        if vals:
            vals = self._apply_transactions_creating_new_cart_line_prepare_vals(
                cart, transactions, vals
            )
            return (0, None, vals)
        return None

    @api.model
    def _apply_transactions_creating_new_cart_line_prepare_vals(
        self, cart: SaleOrder, transactions: list[CartTransaction], values: dict
    ):
        """Post hook allowing to add custom values in cart lines to be created.

        Meant to be overridden
        """
        return values

    @api.model
    def _get_sale_order_line_name(self, product_id):
        product = self.env["product.product"].browse(product_id)
        name = product.name_get()[0][1]
        if product.description_sale:
            name += "\n" + product.description_sale
        return name

    @api.model
    def _prepare_line_from_transactions(
        self, cart: SaleOrder, transactions: list[CartTransaction]
    ):
        """ """
        delta_qty = sum(t.qty for t in transactions)
        product_id = (transactions[0]).product_id
        product_uom = self.env["product.product"].browse(product_id).uom_id
        if float_compare(delta_qty, 0, precision_rounding=product_uom.rounding) <= 0:
            return None
        partner = cart.partner_id
        vals = {
            # Order in this dict is important and must be kept.
            # All computes depending on order_id must be triggered first,
            # to set the currency on the SOL for e.g.
            "order_id": cart.id,
            "product_id": product_id,
            "product_uom_qty": delta_qty,
        }
        ctx_lang = self.env.context.get("lang", partner.lang)
        if partner.lang != ctx_lang:
            product_id = vals["product_id"]
            vals["name"] = self._get_sale_order_line_name(product_id)
        return vals

    @api.model
    def _apply_transactions(self, cart, transactions: list[CartTransaction]):
        """Apply transactions to the given cart."""
        if not transactions:
            return
        cart.ensure_one()
        self._check_transactions(transactions=transactions)
        # prefetch all products
        self.env["product.product"].browse({tx.product_id for tx in transactions})
        grouped_transactions = self._group_transactions(transactions=transactions)
        update_cmds = []
        # here we avoid that each on change on a line trigger all the
        # recompute methods on the SO. These methods will be triggered
        # by the orm into the 'write' process
        for key, trxs in grouped_transactions.items():
            line = cart._get_cart_line(
                **self._apply_transactions_creating_new_cart_line_prepare_vals(
                    cart, trxs, {"product_id": key.product_id}
                )
            )
            if line:
                cmd = self._apply_transactions_on_existing_cart_line(line, trxs)
            else:
                cmd = self._apply_transactions_creating_new_cart_line(cart, trxs)
            if cmd:
                update_cmds.append(cmd)

        all_transaction_uuids = transaction_uuids = [
            str(t.uuid) for t in transactions if t.uuid
        ]
        if cart.applied_cart_api_transaction_uuids:
            all_transaction_uuids = [
                cart.applied_cart_api_transaction_uuids
            ] + transaction_uuids
        vals = {"applied_cart_api_transaction_uuids": ",".join(all_transaction_uuids)}
        if update_cmds:
            vals["order_line"] = update_cmds
        cart.write(vals)

    @api.model
    def _sync_cart(
        self,
        cart: SaleOrder,
        uuid: UUID | None,
        transactions: list[CartTransaction],
    ):
        if not transactions:
            return cart
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        if not uuid or cart.uuid == str(uuid):
            # only apply transaction to a cart if:
            # * no cart_uuid -> new cart
            # * cart_uuid = cart.uuid: Existing cart and transaction for this cart
            self._apply_transactions(cart, transactions)
        return cart

    def _prepare_update_cart_vals(self, data: CartUpdateInput, cart: SaleOrder) -> dict:
        return data._to_sale_order_vals()

    def _update(self, data: CartUpdateInput, uuid: UUID | None):
        cart = self.env["sale.order"]._find_open_cart(
            self.partner.id, str(uuid) if uuid else None
        )
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart(self.partner.id)

        vals = self._prepare_update_cart_vals(data, cart)
        cart.write(vals)

        return cart


def cart_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_cart.cart_router.helper"].new({"partner": partner})


@cart_router.get("/{uuid}")
@cart_router.get("/current")
@cart_router.get("/")
def get(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    uuid: UUID | None = None,
) -> Sale | None:
    """
    Return an empty dict if no cart was found
    """
    cart = helper._get_cart(uuid)
    return Sale.from_sale_order(cart) if cart else Response(status_code=204)


@cart_router.post("/sync/{uuid}", status_code=201, deprecated=True)
@cart_router.post("/{uuid}/sync", status_code=201)
@cart_router.post("/current/sync", status_code=201)
@cart_router.post("/sync", status_code=201)
def sync(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    data: CartSyncInput,
    uuid: UUID | None = None,
) -> Sale | None:
    cart = helper._get_cart(uuid)
    cart = helper._sync_cart(cart, uuid, data.transactions)
    return Sale.from_sale_order(cart) if cart else Response(status_code=204)


@cart_router.post("/new", status_code=201)
def new(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    data: CartSyncInput,
) -> Sale | None:
    """Create a new cart on demand.

    You can use this endpoint to create multiple carts for the same customer.
    """
    cart = helper._sync_cart(None, None, data.transactions)
    return Sale.from_sale_order(cart) if cart else Response(status_code=204)


@cart_router.post("/update/{uuid}", deprecated=True)
@cart_router.post("/{uuid}/update")
@cart_router.post("/current/update")
@cart_router.post("/update")
def update(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    data: CartUpdateInput,
    uuid: UUID | None = None,
) -> Sale:
    cart = helper._update(data, uuid)
    return Sale.from_sale_order(cart)
