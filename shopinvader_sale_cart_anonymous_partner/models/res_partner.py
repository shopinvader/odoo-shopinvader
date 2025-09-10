# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _promote_from_anonymous_partner(self, anonymous_partner):
        """
        Promote an anonymous partner to a real partner
        """
        rv = super()._promote_from_anonymous_partner(anonymous_partner)

        anonymous_cart = (
            self.env["sale.order"].sudo()._find_open_cart(anonymous_partner.id)
        )
        if anonymous_cart:
            anonymous_cart._transfer_cart(self.id)
            anonymous_cart.unlink()

        return rv
