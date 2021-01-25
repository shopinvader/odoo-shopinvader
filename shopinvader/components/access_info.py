# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    """Define access rules to partner from client side."""

    _name = "shopinvader.partner.access"
    _inherit = "base.shopinvader.component"
    _usage = "access.info"
    _apply_on = "res.partner"

    @property
    def service_work(self):
        return getattr(self.work, "service_work", None)

    @property
    def partner(self):
        return getattr(self.work, "partner", None)

    @property
    def invader_partner(self):
        return getattr(self.work, "invader_partner", None)

    @property
    def partner_user(self):
        return getattr(self.work, "partner_user", self.partner)

    @property
    def invader_partner_user(self):
        return getattr(self.work, "invader_partner_user", self.partner)

    def is_main_partner(self):
        return self.partner == self.partner_user

    def is_owner(self, partner_id):
        return partner_id == self.partner_user.id

    def for_profile(self, partner_id):
        info = {"read": True, "update": True, "delete": False}
        if not self.is_main_partner() and partner_id != self.partner_user.id:
            info["update"] = False
        return info

    def for_address(self, address_id):
        info = {"read": True, "update": True, "delete": True}
        if self.partner_user is not None:
            if not self.is_main_partner():
                if not self.is_owner(address_id):
                    info.update({"read": True, "update": False, "delete": False})
                else:
                    # only main partner can delete your address
                    info["delete"] = False
        return info

    def permissions(self):
        """Current user permissions mapping.

        :returns: a dictionary in the format

            {$component_usage: {$method: $permission_flag}}
        """
        if self.partner is None:
            return {"address": {}, "cart": {}}
        return {
            # scope: permissions
            "addresses": {
                # can create addresses only if profile partner is enabled
                "create": self.invader_partner.is_shopinvader_active,
            },
            "cart": {
                # can hit the button to add to cart
                "add_item": self.invader_partner.is_shopinvader_active,
                # can go on w/ checkout steps
                "update_item": self.invader_partner.is_shopinvader_active,
            },
        }
