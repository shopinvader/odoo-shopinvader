# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    _inherit = "shopinvader.partner.access"

    def permissions(self):
        perm = super().permissions()
        if not self.is_main_partner():
            # simple company users cannot add new addresses
            perm["addresses"]["create"] = False
        return perm
