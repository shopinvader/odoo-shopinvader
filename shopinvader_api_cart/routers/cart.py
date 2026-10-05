# Copyright 2022 ACSONE SA/NV
# Copyright 2024 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict, namedtuple
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError
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


@cart_router.post("/new", status_code=201)
def new(
    data: CartSyncInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
) -> Sale | None:
    """Create a new cart on demand.

    You can use this endpoint to create multiple carts for the same customer.
    """
    cart = env["shopinvader_api_cart.cart_router.helper"]._sync_cart(
        partner, None, None, data.transactions
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
                    _(f"Product with id {transaction.product_id} not existing.")
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
        vals.update(cart_line._play_onchanges_cart_line(vals))
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
            vals.update(self.env["sale.order.line"]._play_onchanges_cart_line(vals))
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
    def _get_applied_transaction_uuids(self, cart: SaleOrder) -> set:
        """Return the set of transaction uuids already applied on the cart."""
        if not cart.applied_cart_api_transaction_uuids:
            return set()
        return set(cart.applied_cart_api_transaction_uuids.split(","))

    @api.model
    def _filter_new_transactions(
        self, cart: SaleOrder, transactions: list[CartTransaction]
    ) -> list[CartTransaction]:
        """Drop the transactions already applied on the cart and check that
        the remaining ones were never applied either.

        Transactions are expected in the order they occurred. A client may
        resend a batch that overlaps with what was already synced (for
        example after a lost response), so we skip the leading transactions
        already known and keep everything from the first unknown one on. If
        an already applied transaction appears after that point, the received
        order is inconsistent with what the cart knows: applying it again
        would add the same quantity delta a second time, so we raise a
        UserError.
        """
        applied = self._get_applied_transaction_uuids(cart)
        if not applied:
            return transactions
        boundary = 0
        for index, transaction in enumerate(transactions):
            if transaction.uuid and str(transaction.uuid) in applied:
                boundary = index + 1
            else:
                break
        residual = transactions[boundary:]
        for transaction in residual:
            if transaction.uuid and str(transaction.uuid) in applied:
                raise UserError(
                    _(
                        "Transaction %(uuid)s was already applied to this "
                        "cart but is received out of order."
                    )
                    % {"uuid": transaction.uuid}
                )
        return residual

    @api.model
    def _apply_transactions(self, cart, transactions: list[CartTransaction]):
        """Apply transactions to the given cart."""
        if not transactions:
            return
        cart.ensure_one()
        transactions = self._filter_new_transactions(cart, transactions)
        if not transactions:
            return
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

        new_transaction_uuids = [str(t.uuid) for t in transactions if t.uuid]
        all_transaction_uuids = new_transaction_uuids
        if cart.applied_cart_api_transaction_uuids:
            all_transaction_uuids = [
                cart.applied_cart_api_transaction_uuids
            ] + new_transaction_uuids
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

    def _prepare_update_cart_vals(self, data: CartUpdateInput, cart: SaleOrder) -> dict:
        return data._to_sale_order_vals()

    def _update(self, partner, data, uuid):
        cart = self.env["sale.order"]._find_open_cart(partner.id, uuid)
        if not cart:
            cart = self.env["sale.order"]._create_empty_cart(partner.id)

        vals = self._prepare_update_cart_vals(data, cart)
        cart.write(vals)

        return cart
