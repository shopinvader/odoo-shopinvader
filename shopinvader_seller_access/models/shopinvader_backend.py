from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    seller_access = fields.Boolean(
        "Seller Access", help="Enable seller access on this backend"
    )
    seller_access_group_name = fields.Char(
        "Seller Access Group Name",
        help="Name of the group the authenticated user must provide in the "
        "token groups claim to be considered a seller",
    )
    seller_access_customer_domain = fields.Char(
        "Seller Access Customer Domain",
        default=[("is_shopinvader_active", "=", True)],
        help="Domain used to list all customers a seller can place an order for",
    )
