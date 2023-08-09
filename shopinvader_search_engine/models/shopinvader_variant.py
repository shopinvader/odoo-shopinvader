# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "shopinvader.se.binding"]
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"

    def _get_shop_data(self):
        """Use pre-computed index data if exist."""
        # Normally data always exist but in some special case (like test)
        # it can be not computed yet, so we fall back to computed value
        data = self.get_export_data()
        if data:
            return data
        else:
            return super()._get_shop_data()
