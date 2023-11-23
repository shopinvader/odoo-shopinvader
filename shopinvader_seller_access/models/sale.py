from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    created_by_seller = fields.Boolean(
        string="Created by seller",
        default=False,
        copy=False,
        help="This field is used to know if the sale order has been created by "
        "a seller with create_for",
    )
