# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_qty_step(self):
        items = self.env["product.pricelist.item"].search(
            [
                "|",
                "|",
                "|",
                ("product_id", "=", self.record_id.id),
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("categ_id", "=", self.categ_id.id),
                "&",
                "&",
                ("product_id", "=", False),
                ("categ_id", "=", False),
                ("product_tmpl_id", "=", False),
                "|",
                ("date_start", "<=", fields.datetime.now()),
                ("date_start", "=", False),
                "|",
                ("date_end", ">=", fields.datetime.now()),
                ("date_end", "=", False),
            ]
        )
        return sorted({item.min_quantity for item in items if item.min_quantity > 1})

    def _get_price(
        self, qty=1.0, pricelist=None, fposition=None, company=None, date=None
    ):
        res = super()._get_price(
            qty=qty,
            pricelist=pricelist,
            fposition=fposition,
            company=company,
            date=date,
        )
        if qty == 1.0:
            res["per_qty"] = {
                qty: self._get_price(
                    qty=qty, pricelist=pricelist, fposition=fposition, company=company
                )["value"]
                for qty in self._get_qty_step()
            }
        return res
