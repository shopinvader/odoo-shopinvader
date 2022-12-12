# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.sale.cart.service"

    # ##############
    # implementation
    # ##############

    def _must_charge_delivery_fee_on_order(self):
        """Return true if the delivery fee must be set on the cart at
        the same time as the method or false if delivery fee are applied on
        delivery.
        """
        return self.shopinvader_backend.charge_delivery_fee_on_order
