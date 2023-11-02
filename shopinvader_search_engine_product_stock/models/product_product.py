# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_data = fields.Json(compute="_compute_stock_data")

    def _prepare_stock_data(self):
        self.ensure_one()
        index_id = self._context.get("index_id", False)
        if index_id:
            index = self.env["se.index"].browse(index_id)
            stock_field = index.product_stock_field_id.name
            return {"qty": self[stock_field]}
        return {"qty": None}

    @api.depends_context("index_id")
    def _compute_stock_data(self):
        result = defaultdict(dict)
        index_id = self.env.context.get("index_id", False)
        if index_id:
            index = self.env["se.index"].browse(index_id)
            loc_records = self._filter_by_index()
            for (wh_key, wh_ids) in index._get_warehouse_list_for_export().items():
                for loc_record in loc_records.with_context(warehouse=wh_ids):
                    result[loc_record.id][wh_key] = loc_record._prepare_stock_data()
        for record in self:
            record.stock_data = result[record.id]

    def synchronize_all_binding_stock_level(self, company_id=None):
        """Compute new stock information and update index data.

        If data changed and binding is in done state it forces it to 'to_export'.
        :return:
        """
        # Use `sudo` because this action might be triggered
        # from a low access level user (eg: external user on portal/website).
        # In any case, the real operation is done w/ the backend user below.

        # ensure user company propagation if the method has bee delayed...
        # this feature should be provide by queue job ...
        # see https://github.com/OCA/queue/issues/363
        products = self
        if company_id:
            products = self.with_company(company_id)

        all_bindinds = products.mapped("se_binding_ids")
        indexes = all_bindinds.mapped("index_id")
        for index in indexes:
            for product in products.with_context(index_id=index.id)._filter_by_index():
                binding = product.sudo().se_binding_ids.filtered(
                    lambda b, i=index: b.index_id == i
                )
                if not binding.data:
                    # this binding has been not yet computed
                    # so we do not care to update it as it's not yet
                    # on the site. The right stock qty will be exported
                    # at its first export.
                    continue
                data = binding.data
                product_stock_data = product.stock_data
                if data["stock"] != product_stock_data:
                    data["stock"] = product_stock_data
                    vals = {"data": data}
                    if index.synchronize_stock == "immediatly":
                        binding.write(vals)
                        binding.export_record()
                    elif index.synchronize_stock == "in_batch":
                        if binding.state == "done":
                            vals["state"] = "to_export"
                        binding.write(vals)
