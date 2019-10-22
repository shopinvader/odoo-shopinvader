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
        return self.work.service_work

    @property
    def partner(self):
        # this component might be called from a service component
        # which has not being initialized in the scope of a complete REST API
        # work context.
        # Eg: called from a payment.transaction event handler.
        return getattr(self.work.service_work, "partner", None)

    @property
    def partner_user(self):
        # this component might be called from a service component
        # which has not being initialized in the scope of a complete REST API
        # work context.
        # Eg: called from a payment.transaction event handler.
        return getattr(self.work.service_work, "partner_user", None)

    def is_main_partner(self):
        return self.partner == self.partner_user

    def profile(self, partner):
        return {"read": True, "update": True, "delete": False}

    def address(self, address_id):
        return {"read": True, "update": True, "delete": True}

    def permission(self, partner):
        if self.partner is None:
            return {"address": {}, "purchase": {}}
        return {
            # scope: permissions
            "address": {
                # can create addresses only if profile partner is enabled
                "create": self.partner.shopinvader_enabled
            },
            "purchase": {
                # can hit the button to add to cart
                "add_to_cart": self.partner.shopinvader_enabled,
                # can go on w/ checkout steps
                "checkout": self.partner.shopinvader_enabled,
            },
        }
