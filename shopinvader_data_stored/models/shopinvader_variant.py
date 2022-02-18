# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "jsonify.stored.mixin"]
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"

    def _jsonify_get_exporter(self):
        return self.index_id.exporter_id

    def _get_shop_data(self):
        """Use pre-computed index data."""
        return self.jsonified_data
