# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    se_backend_id = fields.Many2one(
        comodel_name="se.backend",
        string="Search Engine Backend",
        help="Search Engine backend configuration to use",
    )
    index_ids = fields.One2many("se.index", related="se_backend_id.index_ids")

    @api.model
    def _get_default_models(self):
        domain = self.env["se.index"]._get_model_domain()
        return self.env["ir.model"].search(domain)

    @api.multi
    def force_recompute_all_binding_index(self):
        self.sudo_tech().mapped(
            "se_backend_id.index_ids"
        ).force_recompute_all_binding()
        return True

    @api.multi
    def force_batch_export_index(self):
        for index in self.sudo_tech().mapped("se_backend_id.index_ids"):
            index.force_batch_export()
        return True

    @api.multi
    def clear_index(self):
        for index in self.mapped("se_backend_id.index_ids"):
            index.clear_index()
        return True

    @api.multi
    def add_missing_index(self):
        self.ensure_one()
        ir_models = self._get_default_models()
        index_obj = self.env["se.index"]
        ir_export_obj = self.env["ir.exports"]
        if not self.se_backend_id:
            return
        for model in ir_models:
            for lang in self.lang_ids:
                ir_export = ir_export_obj.search(
                    [("resource", "=", model.model)], limit=1
                )
                if ir_export and not self.index_ids.filtered(
                    lambda i: i.lang_id == lang and i.model_id == model
                ):
                    index_obj.create(
                        {
                            "backend_id": self.se_backend_id.id,
                            "model_id": model.id,
                            "lang_id": lang.id,
                            "exporter_id": ir_export.id,
                        }
                    )
        return True

    @api.multi
    def force_resynchronize_index(self):
        self.mapped("se_backend_id.index_ids").resynchronize_all_bindings()

    @api.multi
    def export_index_settings(self):
        self.mapped("se_backend_id.index_ids").export_settings()
