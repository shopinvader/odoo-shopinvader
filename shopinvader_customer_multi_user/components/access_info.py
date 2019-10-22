# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    _inherit = "shopinvader.partner.access"

    def profile(self, partner):
        info = super().profile(partner)
        if not self.is_main_partner() and partner != self.partner_user:
            info.update({"update": False})
        return info

    def address(self, address_id):
        info = super().address(address_id)
        if self.partner_user is not None:
            address_owner = address_id == self.partner_user.id
            if not self.is_main_partner() and not address_owner:
                info.update({"read": True, "update": False, "delete": False})
        return info

    def permission(self, partner):
        perm = super().permission(partner)
        if not self.is_main_partner():
            # simple company users cannot add new addresses
            perm["address"]["create"] = False
        return perm
