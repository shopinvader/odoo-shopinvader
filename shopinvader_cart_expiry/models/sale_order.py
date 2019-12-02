# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    cart_expiration_date = fields.Datetime(
        compute="_compute_cart_expiration_date",
        help="Technical field to help passing expiration date to cart",
    )

    @api.depends(
        "shopinvader_backend_id.cart_expiry_delay", "typology", "write_date"
    )
    def _compute_cart_expiration_date(self):
        """
        Compute the cart expiration date
        :return:
        """
        carts = self.filtered(
            lambda s: s.shopinvader_backend_id
            and s.shopinvader_backend_id.cart_expiry_delay != 0
            and s.typology == "cart"
        )
        for cart in carts:
            backend = cart.shopinvader_backend_id
            delta_arg = {
                backend.cart_expiry_delay_unit: backend.cart_expiry_delay
            }
            expiration_date = cart.write_date + timedelta(**delta_arg)
            cart.cart_expiration_date = expiration_date
