# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import OrderedDict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from odoo import _, api, models
from odoo.exceptions import MissingError
from odoo.tools import float_compare

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale.models.sale_order_line import SaleOrderLine
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import CartSyncInput, CartTransaction, CartUpdateInput

cart_router = APIRouter(tags=["carts"])


@cart_router.get("/{uuid}")
@cart_router.get("/current")
@cart_router.get("/")
def get(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale | None:
    """
    Return an empty dict if no cart was found
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    return Sale.from_sale_order(cart) if cart else Response(status_code=204)


@cart_router.post("/sync/{uuid}", status_code=201, deprecated=True)
@cart_router.post("/{uuid}/sync", status_code=201)
@cart_router.post("/current/sync", status_code=201)
@cart_router.post("/sync", status_code=201)
def sync(
    data: CartSyncInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale | None:
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    cart = env["shopinvader_api_cart.cart_router.helper"]._sync_cart(
        partner, cart, str(uuid) if uuid else None, data.transactions
    )
    return Sale.from_sale_order(cart) if cart else Response(status_code=204)


@cart_router.post("/update/{uuid}", deprecated=True)
@cart_router.post("/{uuid}/update")
@cart_router.post("/current/update")
@cart_router.post("/update")
def update(
    data: CartUpdateInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale:
    cart = env["shopinvader_api_cart.cart_router.helper"]._update(
        partner, data, str(uuid) if uuid else None
    )

    return Sale.from_sale_order(cart)


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_cart.cart_router.helper"
    _description = "ShopInvader API Cart Router Helper"

    @api.model
    def _check_transactions(self, transactions: list[CartTransaction]):
        """Check if the transactions info are valid.

        This method car be extended to validate if the product_id is
        sellable via the rest api, or ...
        """
        for transaction in transactions:
            if not self.env["product.product"].browse(transaction.product_id).exists():
                raise MissingError(
                    _(f"Product with id {transaction.product_id} not existing.")
                )

    @api.model
    def _group_transactions_by_product_id(self, transactions: list[CartTransaction]):
        """
        Gather together transactions that are linked to the same product.
        """
        # take an ordered dict to ensure to create lines into the same
        # order as the transactions list
        transactions_by_product_id = OrderedDict()
        for trans in transactions:
            product_id = trans.product_id
            transactions = transactions_by_product_id.get(product_id)
            if not transactions:
                transactions = []
                transactions_by_product_id[product_id] = transactions
            transactions.append(trans)
        return transactions_by_product_id

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
        vals.update(cart_line._play_onchanges_cart_line(vals))
        return (1, cart_line.id, vals)

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
            vals.update(self.env["sale.order.line"]._play_onchanges_cart_line(vals))
            return (0, None, vals)
        return None

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
            # When creating the transaction we call play_onchanges().
            # These onchanges will be played following the order defined here.
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
        transactions_by_product_id = self._group_transactions_by_product_id(
            transactions=transactions
        )
        update_cmds = []
        with self.env.norecompute():
            # prefetch all products
            self.env["product.product"].browse(transactions_by_product_id.keys())
            # here we avoid that each on change on a line trigger all the
            # recompute methods on the SO. These methods will be triggered
            # by the orm into the 'write' process
            for product_id, trxs in transactions_by_product_id.items():
                line = cart._get_cart_line(product_id)
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
        partner: ResPartner,
        cart: SaleOrder,
        uuid: str,
        transactions: list[CartTransaction],
    ):
        if not transactions:
            return cart
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart(partner.id)
        if not uuid or cart.uuid == uuid:
            # only apply transaction to a cart if:
            # * no cart_uuid -> new cart
            # * cart_uuid = cart.uuid: Existing cart and transaction for this cart
            self._apply_transactions(cart, transactions)
        return cart

    def _update(self, partner, data, uuid):
        cart = self.env["sale.order"]._find_open_cart(partner.id, uuid)
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart()
        cart.write(data.convert_to_sale_write())
        return cart
