# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    _inherit = "shopinvader.partner.access"

    def permissions(self):
        perm = super().permissions()
        perm["users"] = {"manage": self.invader_partner_user.is_users_manager}
        return perm

    def for_address(self, address_id):
        info = super().for_address(address_id)
        # Who can edit
        # - owner
        # - admin account
        if self.partner_user is not None:
            can_manage = (
                self.is_owner(address_id) or self.invader_partner_user.is_admin_account
            )
            if can_manage:
                info.update({"read": True, "update": True, "delete": True})
            else:
                info.update({"read": True, "update": False, "delete": False})
        return info
