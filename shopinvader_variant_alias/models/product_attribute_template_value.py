# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"
    shopinvader_alias = fields.Char(
        related="product_attribute_value_id.shopinvader_alias"
    )
