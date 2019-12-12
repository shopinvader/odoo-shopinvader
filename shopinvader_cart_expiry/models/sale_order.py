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

    def _is_expiring_cart(self):
        return (
            self.shopinvader_backend_id
            and self.shopinvader_backend_id.cart_expiry_delay != 0
            and self.typology == "cart"
        )

    @api.depends(
        "shopinvader_backend_id.cart_expiry_delay", "typology", "write_date"
    )
    def _compute_cart_expiration_date(self):
        """
        Compute the cart expiration date
        :return:
        """
        for order in self:
            if order._is_expiring_cart():
                trigger_date = (
                    order.write_date
                    and order.write_date
                    or fields.Datetime.from_string(fields.Datetime.now())
                )
                backend = order.shopinvader_backend_id
                delta_arg = {
                    backend.cart_expiry_delay_unit: backend.cart_expiry_delay
                }
                expiration_date = trigger_date + timedelta(**delta_arg)
                order.cart_expiration_date = expiration_date
