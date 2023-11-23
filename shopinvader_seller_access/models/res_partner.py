from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    seller_available_customer_domain = fields.Char(
        "Seller Available Customer Domain",
        default=[],
        help="Domain used to restrict the list of customers a seller can access",
    )
