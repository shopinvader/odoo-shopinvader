# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderCategory(models.Model):
    _inherit = ["shopinvader.category", "jsonifier.stored.mixin"]
    _name = "shopinvader.category"

    def get_shop_data(self):
        # Use pre-computed index data
        return self.jsonified_data

    def _jsonify_get_exporter(self):
        return self.backend_id.category_exporter_id

    def _jobify_json_data_compute_default_channel(self):
        if self.backend_id.category_data_compute_channel_id:
            return self.backend_id.category_data_compute_channel_id.complete_name
        return super()._jobify_json_data_compute_default_channel()
