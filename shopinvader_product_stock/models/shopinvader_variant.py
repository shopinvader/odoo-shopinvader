# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    stock_data = Serialized(compute="_compute_stock_data")

    def _get_stock_export_key(self):
        self.ensure_one()
        line = self.env["ir.exports.line"].search(
            [
                ("export_id", "=", self.index_id.exporter_id.id),
                ("name", "=", "stock_data"),
            ]
        )
        if line.target:
            return line.target.split(":")[1]
        else:
            return line.name

    def _prepare_stock_data(self):
        stock_field = self.backend_id.product_stock_field_id.name
        return {"qty": self[stock_field]}

    def _compute_stock_data(self):
        result = defaultdict(dict)
        for backend in self.mapped("backend_id"):
            loc_records = self.filtered(lambda s: s.backend_id == backend)
            for (
                wh_key,
                wh_ids,
            ) in backend._get_warehouse_list_for_export().items():
                for loc_record in loc_records.with_context(warehouse=wh_ids):
                    result[loc_record.id][
                        wh_key
                    ] = loc_record._prepare_stock_data()
        for record in self:
            record.stock_data = result[record.id]
