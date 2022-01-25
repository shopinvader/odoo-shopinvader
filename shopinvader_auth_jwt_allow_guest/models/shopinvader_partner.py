from odoo import _, api, fields, models


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    is_guest = fields.Boolean("Is guest user", default=False)
