# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    uuid = fields.Char(string="EShop Unique identifier", readonly=True)
    applied_transaction_uuids = fields.Char(readonly=True)

    def _check_transactions(self, transactions):
        """Entry point to check if the transactions info are valid.

        This method car be extended to validate the the product_id is
        sellable via the rest api, or ...
        """
        self.ensure_one()

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
        all_transaction_uuids = transaction_uuids = [t["uuid"] for t in transactions]
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
            product_id = trans["product_id"]
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
