from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    merge_cart_on_transfer = fields.Boolean(
        string="Merge Cart on Transfer",
        help="If checked, the cart will be merged with the existing one if "
        "any on transfer.",
    )
