# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
        domain = self.env["se.index"]._model_id_domain()
        return self.env["ir.model"].search(domain)

    def force_recompute_all_binding_index(self):
        self.sudo_tech().mapped("se_backend_id.index_ids").force_recompute_all_binding()
        return True

    def force_batch_export_index(self):
        for index in self.sudo_tech().mapped("se_backend_id.index_ids"):
            index.force_batch_export()
        return True

    def clear_index(self):
        for index in self.mapped("se_backend_id.index_ids"):
            index.clear_index()
        return True

    def add_missing_index(self):
        _logger.warning("DEPRECATED: add_missing_index, use action_add_missing_indexes")
        self.action_add_missing_indexes()

    def action_add_missing_indexes(self):
        self.ensure_one()
        if not self.se_backend_id:
            return
        self._add_missing_indexes()

    def _add_missing_indexes(self):
        ir_models = self._get_default_models()
        new_indexes = self.env["se.index"].browse()

        # Process lang agnostic indexes first
        lang_agnostic_ir_models = ir_models.browse()
        for ir_model in ir_models:
            model_class = self.env[ir_model.model]
            if getattr(model_class, "_se_index_lang_agnostic", False):
                lang_agnostic_ir_models |= ir_model
                new_indexes |= self._create_missing_index(ir_model)

        # Process lang-specific indexes
        for ir_model in ir_models:
            if ir_model.id in lang_agnostic_ir_models.ids:
                continue
            for lang in self.lang_ids:
                new_indexes |= self._create_missing_index(ir_model, lang_record=lang)
        return new_indexes

    def _create_missing_index(self, ir_model, lang_record=None):
        new_index = self.env["se.index"]
        ir_export = self._get_index_export_config(ir_model)
        if not ir_export:
            _logger.debug("Cannot create index automatically: no ir.export found.")
            return new_index

        if self._check_index_exists(ir_model, lang_record=lang_record):
            return new_index

        values = self._get_create_index_values(
            ir_model, ir_export, lang_record=lang_record
        )
        return self.env["se.index"].create(values)

    def _get_index_export_config(self, ir_model):
        return self.env["ir.exports"].search(
            [("resource", "=", ir_model.model)], limit=1
        )

    def _check_index_exists(self, ir_model, lang_record=None):
        exists_domain = [("model_id", "=", ir_model.id)]
        if lang_record:
            exists_domain.append(("lang_id", "=", lang_record.id))
        return bool(self.index_ids.filtered_domain(exists_domain))

    def _get_create_index_values(self, ir_model, ir_export, lang_record=None):
        return {
            "backend_id": self.se_backend_id.id,
            "model_id": ir_model.id,
            "lang_id": lang_record.id if lang_record else False,
            "exporter_id": ir_export.id,
        }

    def force_resynchronize_index(self):
        self.mapped("se_backend_id.index_ids").resynchronize_all_bindings()

    def export_index_settings(self):
        self.mapped("se_backend_id.index_ids").export_settings()
