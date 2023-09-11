# Copyright 2023 Akretion (http://www.akretion.com)
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import UserError
from odoo.tools.translate import _

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _check_allowed_product(self, cart, params):
        product = self.env["product.product"].browse(params["product_id"])
        if not product._add_to_cart_allowed(
            self.shopinvader_backend, partner=self.partner
        ):
            raise UserError(_("Product %s is not allowed") % product.name)

    def _add_item(self, cart, params):
        self._check_allowed_product(cart, params)
        return super()._add_item(cart, params)
