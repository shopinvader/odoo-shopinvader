# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid
from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import MissingError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    uuid = fields.Char(string="EShop Unique identifier", readonly=True)
    applied_transaction_uuids = fields.Char(readonly=True)

    @api.model
    def _play_onchanges_cart(self, vals):
        return self.sudo().play_onchanges(vals, vals.keys())

    def _sync_cart(self, cart_uuid, transactions):
        cart = self.env["sale.order"]._find_open_cart(cart_uuid)
        if not cart and transactions:
            cart = self.env["sale.order"]._create_empty_cart(
                self.env.context.get("authenticated_partner_id")
            )
        if not cart_uuid or cart.uuid == cart_uuid:
            # only apply transaction to a cart if:
            # * no cart_uuid -> new cart
            # * cart_uuid = cart.uuid: Existing cart and transaction for this cart
            cart._apply_transactions(transactions)
        return cart

    def _check_transactions(self, transactions):
        """Entry point to check if the transactions info are valid.

        This method car be extended to validate if the product_id is
        sellable via the rest api, or ...
        """
        self.ensure_one()
        for transaction in transactions:
            if not self.env["product.product"].browse(transaction.product_id).exists():
                raise MissingError(
                    _(f"Product with id {transaction.product_id} not existing.")
                )

    def _apply_transactions(self, transactions):
        """Apply transactions from cart service.

        Transactions is a list of dict with 'product_id','qty' and
        uuid keys
        """
        if not transactions:
            return
        self.ensure_one()
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
                line = self._get_cart_line(product_id)
                if line:
                    cmd = line._transactions_to_record_write(trxs)
                else:
                    cmd = self.env["sale.order.line"]._transactions_to_record_create(
                        self, trxs
                    )
                if cmd:
                    update_cmds.append(cmd)
        all_transaction_uuids = transaction_uuids = [
            t.uuid for t in transactions if t.uuid
        ]
        if self.applied_transaction_uuids:
            all_transaction_uuids = [self.applied_transaction_uuids] + transaction_uuids
        vals = {"applied_transaction_uuids": ",".join(all_transaction_uuids)}
        if update_cmds:
            vals["order_line"] = update_cmds
        self.write(vals)

    @api.model
    def _group_transactions_by_product_id(self, transactions):
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

    def _get_cart_line(self, product_id):
        self.ensure_one()
        return self.order_line.filtered(
            lambda l, product_id=product_id: l.product_id.id == product_id
        )[:1]

    @api.model
    def _get_open_cart_domain(self, partner_id, uuid=None):
        domain = [
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
            ("partner_id", "=", partner_id),
        ]
        if uuid:
            domain.append(("uuid", "=", uuid))
        return domain

    @api.model
    def _find_open_cart(self, uuid=None):
        authenticated_partner_id = self.env.context.get("authenticated_partner_id")
        if not authenticated_partner_id and not uuid:
            # uuid is required for anonymous users
            return self.browse()
        domain = self._get_open_cart_domain(authenticated_partner_id, uuid=uuid)
        cart = self.search(domain, limit=1)
        if not cart and authenticated_partner_id and uuid:
            # maybe a current cart exists with another uuid
            domain = self._get_open_cart_domain(authenticated_partner_id, uuid=None)
            cart = self.search(domain, limit=1)
        return cart

    @api.model
    def _get_default_pricelist_id(self):
        """Return the pricelist to use if no one found on the partner

        By default we return the one defined on the anonymous user partner.
        Since the anonymous partner is inactive, we must disable the active test
        to be able to read the property product pricelist
        """
        return (
            self.env.ref("base.public_user")
            .partner_id.with_context(active_test=False)
            .property_product_pricelist.id
        )

    @api.model
    def _prepare_cart(self, partner_id):
        vals = {
            "uuid": str(uuid.uuid4()),
            "typology": "cart",
            "partner_id": partner_id,
        }
        vals.update(self._play_onchanges_cart(vals))
        if not vals.get("pricelist_id"):
            vals["pricelist_id"] = self._get_default_pricelist_id()
        return vals

    def _create_empty_cart(self, partner_id):
        vals = self._prepare_cart(partner_id)
        return self.create(vals)
