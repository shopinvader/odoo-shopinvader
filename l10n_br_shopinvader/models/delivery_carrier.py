#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Carrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_period = fields.Char(string="Delivery period")

    def rate_shipment(self, order):
        """Compute the price of the order shipment

        :param order: record of sale.order
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
                       # TODO maybe the currency code?
        """
        self.ensure_one()
        res = super().rate_shipment(order)
        # If the Total Freight Value is filled in, it has
        # preference over the Calculated value.
        res["calculated_price"] = res["price"]
        if order.amount_freight_value > 0.0:
            res["price"] = order.amount_freight_value

        return res
