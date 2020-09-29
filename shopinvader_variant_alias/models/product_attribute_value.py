# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"
    shopinvader_alias = fields.Char(
        help="Name under which this attribute will be exported to ShopInvader."
    )
