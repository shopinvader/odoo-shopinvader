# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "jsonifier.stored.mixin"]
    _name = "shopinvader.variant"

    def get_shop_data(self):
        # Use pre-computed index data
        return self.jsonified_data

    def _jsonify_get_exporter(self):
        return self.backend_id.variant_exporter_id

    def _jobify_json_data_compute_default_channel(self):
        if self.backend_id.variant_data_compute_channel_id:
            return self.backend_id.variant_data_compute_channel_id.complete_namme
        return super()._jobify_json_data_compute_default_channel()

    def _json_data_compute_get_all_langs(self, table=None):
        # the lang field comes from s.product which in turn gets it from abstract.url
        return super()._json_data_compute_get_all_langs(table="shopinvader_product")
