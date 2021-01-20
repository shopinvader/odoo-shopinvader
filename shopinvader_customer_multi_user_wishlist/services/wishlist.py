# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WishlistService(Component):
    _inherit = "shopinvader.wishlist.service"

    def _get_add_to_cart_wizard(self, cart, record):
        wizard = super()._get_add_to_cart_wizard(cart, record)
        return wizard.with_context(
            allowed_order_partner_ids=self._allowed_order_partners().ids
        )

    def _allowed_order_partners(self):
        # In a multi user context, the user might see wishlist
        # that she/he does not own.
        # Make sure that if they can see the wishlist
        # they can also add it to a cart.
        # Validate wishlist partner based on partner domain
        invader_partner = self.invader_partner_user
        possible_partners = (
            self.partner_user
            | invader_partner.parent_id
            | invader_partner.main_partner_id
        )
        domain = invader_partner._make_partner_domain("id")
        return possible_partners.filtered_domain(domain)
