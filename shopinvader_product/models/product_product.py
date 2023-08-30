# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .tools import sanitize_attr_name


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_attributes = fields.Serialized(
        compute="_compute_variant_attributes", string="Shopinvader Attributes"
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_attribute_value_ids",
        readonly=True,
    )

    def _compute_variant_attributes(self):
        for record in self:
            variant_attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                variant_attributes[sanitized_key] = att_value.name
            record.variant_attributes = variant_attributes

    @api.depends("product_template_attribute_value_ids")
    def _compute_attribute_value_ids(self):
        for record in self:
            record.attribute_value_ids = record.mapped(
                "product_template_attribute_value_ids.product_attribute_value_id"
            )
