# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "jsonify.stored.mixin"]
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"

    def get_shop_data(self):
        # Use pre-computed index data
        return self.jsonified_data
