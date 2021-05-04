# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    _inherit = "shopinvader.partner.access"

    def for_wishlist(self, wishlist):
        info = super().for_wishlist(wishlist)
        if self.partner_user is not None:
            if self._can_manage_wishlist(wishlist):
                info.update({"read": True, "update": True, "delete": True})
            else:
                info.update({"read": True, "update": False, "delete": False})
        return info

    def _can_manage_wishlist(self, wishlist):
        return (
            self.is_owner(wishlist.partner_id.id)
            or self.invader_partner_user.is_admin_account
        )
