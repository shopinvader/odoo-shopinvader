from odoo import fields, models


class OtherCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[
            ("other", "Other"),
        ],
        ondelete={
            "other": lambda recs: recs.write(
                {
                    "delivery_type": "fixed",
                    "fixed_price": 0,
                }
            )
        },
    )
    per_unit_price = fields.Float("Per Unit Price", default=10)

    def other_rate_shipment(self, order):
        # Return a test price of per_unit_price per item
        return {
            "success": True,
            "price": self.per_unit_price
            * sum(order.order_line.mapped("product_uom_qty")),
            "error_message": False,
            "warning_message": False,
        }
