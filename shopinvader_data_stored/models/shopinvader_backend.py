# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


def _default_m2o_from_xid(env, xid):
    rec = env.ref(xid, False)
    return rec.id if rec else None


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    frontend_data_source = fields.Selection(selection_add=[("odoo", "Odoo")])
    variant_exporter_id = fields.Many2one(
        comodel_name="ir.exports",
        domain=[("resource", "=", "shopinvader.variant")],
        default=lambda self: self._default_variant_exporter_id(),
    )
    variant_data_compute_channel_id = fields.Many2one(
        comodel_name="queue.job.channel",
        default=lambda self: self._default_variant_channel_id(),
    )
    category_exporter_id = fields.Many2one(
        comodel_name="ir.exports",
        domain=[("resource", "=", "shopinvader.category")],
        default=lambda self: self._default_category_exporter_id(),
    )
    category_data_compute_channel_id = fields.Many2one(
        comodel_name="queue.job.channel",
        default=lambda self: self._default_category_channel_id(),
    )

    def _default_variant_exporter_id(self):
        xid = "shopinvader.ir_exp_shopinvader_variant"
        return _default_m2o_from_xid(self.env, xid)

    def _default_category_exporter_id(self):
        xid = "shopinvader.ir_exp_shopinvader_category"
        return _default_m2o_from_xid(self.env, xid)

    def _default_variant_channel_id(self):
        xid = "shopinvader_data_stored.channel_jsonify_stored_variant"
        return _default_m2o_from_xid(self.env, xid)

    def _default_category_channel_id(self):
        xid = "shopinvader_data_stored.channel_jsonify_stored_category"
        return _default_m2o_from_xid(self.env, xid)

    def force_recompute_all(self):
        self.ensure_one()
        json_mixin = self.env["jsonifier.stored.mixin"]
        domain = [("backend_id", "=", self.id)]
        for model_name in self._force_recompute_all_models():
            job_params = {
                "channel": self._channel_for_model(model_name),
            }
            json_mixin.cron_update_json_data_for(
                model_name,
                domain=domain,
                job_params=job_params,
            )
        return True

    def _force_recompute_all_models(self):
        return (
            x
            for x in self.env["jsonifier.stored.mixin"]._inherit_children
            if x.startswith("shopinvader.")
        )

    def _channel_for_model(self, model):
        return {
            "shopinvader.variant": self.variant_data_compute_channel_id.complete_name,
            "shopinvader.category": self.category_data_compute_channel_id.complete_name,
        }.get(model)
