# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    charge_delivery_fee_on_order = fields.Boolean(
        default=True,
        help="If true, delivery fee will be computed and charged on order, "
        "otherwise delivery fee will be charged on delivery.",
    )
