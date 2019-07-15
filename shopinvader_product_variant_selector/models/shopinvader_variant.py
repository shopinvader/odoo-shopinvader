# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    variant_selector = fields.Serialized(
        compute="_compute_variant_selector", string="Shopinvader Selector"
    )

    def _prepare_selector_value(self, variant, value):
        return {
            "name": value.name,
            "sku": variant.default_code or "",
            "available": variant.active,
            "selected": variant == self,
        }

    def _get_available_attribute_value(self, attribute):
        for attribute_line in self.attribute_line_ids:
            if attribute_line.attribute_id == attribute:
                return attribute_line.value_ids
        return self.env["product.attribute.value"].browse(False)

    def _get_matching_variant(self, values):
        """Return the first vairant that match the values"""
        for variant in self.shopinvader_variant_ids:
            if values <= variant.attribute_value_ids:
                return variant
        return self.env["shopinvader.variant"].browse(False)

    def _get_selector_for_attribute(self, attribute, restrict_values=None):
        if restrict_values is None:
            restrict_values = self.env["product.attribute.value"].browse()
        res = {"name": attribute.name, "values": []}
        for value in self._get_available_attribute_value(attribute):
            variant = self._get_matching_variant(value + restrict_values)
            res["values"].append(self._prepare_selector_value(variant, value))
        return res

    def _compute_variant_selector(self):
        attributes = self.env["product.attribute"].search([])
        for record in self:
            data = []
            p_values = record.attribute_value_ids
            p_attrs = p_values.mapped("attribute_id")
            restrict_values = self.env["product.attribute.value"].browse(False)
            for attribute in attributes:
                if attribute in p_attrs:
                    data.append(
                        record._get_selector_for_attribute(
                            attribute, restrict_values
                        )
                    )
                    for value in p_values:
                        if value.attribute_id == attribute:
                            restrict_values += value
                            break
            record.variant_selector = data
