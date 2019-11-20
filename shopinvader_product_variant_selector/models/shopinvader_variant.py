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

    # TODO we should do an integration with
    # shopinvader_product_state to be able to show the
    # stock information
    # shopinvader_product_stock_variant_selector
    # should inherit this method
    def _prepare_selector_value(self, variant, value):
        return {
            "name": value.name,
            "sku": variant.default_code or "",
            "available": variant.active,
            "selected": variant == self,
        }

    def _get_matching_variant(self, values):
        """Return the first variant that matches the values."""
        for variant in self.shopinvader_variant_ids:
            if values <= variant.attribute_value_ids:
                return variant
        return self.env["shopinvader.variant"].browse()

    def _get_selector_for_attribute(self, previous_attributes, attribute):
        """This method return the attribute selector for the attribute
        For all value available for this attribute we search the variant that
        match this value and use it for filling the selector information
        """
        res = {"name": attribute.name, "values": []}
        values = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id == attribute
        ).value_ids

        # These are the minimal value that the variant must match
        # as the previous attribute have been selected
        minimal_values = self.attribute_value_ids.filtered(
            lambda v: v.attribute_id in previous_attributes
        )

        for value in values:
            if value in self.attribute_value_ids:
                variant = self
            else:
                # We try first to choose a variant that only have a
                #  variation of current attribute.
                variant = self._get_matching_variant(
                    self.attribute_value_ids - values + value
                )

                if not variant:
                    # If there is no matching variant, we choose a variant
                    #  with more variation but match previous attribute selected
                    variant = self._get_matching_variant(
                        minimal_values + value
                    )
            res["values"].append(self._prepare_selector_value(variant, value))

        return res

    def _compute_variant_selector(self):
        for record in self:
            data = []
            attributes = record.mapped(
                "attribute_value_ids.attribute_id"
            ).sorted("sequence")
            previous_attributes = self.env["product.attribute"].browse()
            for attribute in attributes:
                data.append(
                    record._get_selector_for_attribute(
                        previous_attributes, attribute
                    )
                )
                previous_attributes |= attribute
            record.variant_selector = data
