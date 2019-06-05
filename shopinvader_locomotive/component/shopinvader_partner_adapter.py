# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopinvaderPartnerAdapter(Component):
    _name = "shopinvader.partner.adapter"
    _inherit = "locomotive.content.adapter"

    _apply_on = "shopinvader.partner"
    _content_type = "customers"
