# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons.shopinvader.models.tools import sanitize_attr_name


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"
    shopinvader_alias = fields.Char(
        help="Name under which this attribute will be exported to ShopInvader."
    )


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"
    shopinvader_alias = fields.Char(
        related="product_attribute_value_id.shopinvader_alias"
    )


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _compute_variant_attributes(self):
        """For any attribute value that has a shopinvader_alias,
           overwrites the existing values with it.
        """
        res = super(ShopinvaderVariant, self)._compute_variant_attributes()
        for record in self.filtered("attribute_value_ids.shopinvader_alias"):
            variant_attributes = record.variant_attributes
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                if att_value.shopinvader_alias:
                    variant_attributes[
                        sanitized_key
                    ] = att_value.shopinvader_alias
            record.variant_attributes = variant_attributes
        return res  # res is None, thank you pylint.
