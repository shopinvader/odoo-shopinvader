# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.shopinvader.models.tools import sanitize_attr_name


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

    def _prepare_variant_name_and_short_name(self):
        # Override short name to take into account alias
        short_name = self._prepare_attribute_alias_short_name()
        full_name = self.shopinvader_display_name
        if short_name:
            full_name += " (%s)" % short_name
        return full_name, short_name

    def _prepare_attribute_alias_short_name(self):
        self.ensure_one()
        short_name = ""
        attributes = []
        for key in self.variant_attributes:
            attributes.append(self.variant_attributes[key])
        if attributes:
            short_name = ", ".join(attributes)
        return short_name
