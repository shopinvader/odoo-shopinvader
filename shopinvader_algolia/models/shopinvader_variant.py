# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    @api.model
    def _get_facetting_values(self, se_bakend, lang):
        return self.env["shopinvader.product"]._get_facetting_values(
            se_bakend, lang
        )
