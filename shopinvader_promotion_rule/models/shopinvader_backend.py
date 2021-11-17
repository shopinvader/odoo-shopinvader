# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    always_apply_promotion = fields.Boolean(
        default=True,
        help="Uncheck this if you want to not apply promotion on init cart step",
    )
