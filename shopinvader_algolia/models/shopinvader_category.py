# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ShopinvaderCategory(models.Model):
    _inherit = "shopinvader.category"

    @api.model
    def _get_facetting_values(self, se_backend):
        return ["id", "level", "parent.id", "redirect_url_key", "url_key"]
