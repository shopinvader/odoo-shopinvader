# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models
from odoo.addons.shopinvader.models.tools import sanitize_attr_name


class ProductFilter(models.Model):
    _inherit = "product.filter"

    based_on = fields.Selection(
        selection_add=[("custom_attribute", "Custom Attribute")]
    )
    custom_attribute_id = fields.Many2one(
        string="Attribute", comodel_name="attribute.attribute"
    )

    def _build_display_name(self):
        if self.based_on == "custom_attribute":
            return (
                "attributes.%s"
                % sanitize_attr_name(self.custom_attribute_id)[2:]
            )
        else:
            return super(ProductFilter, self)._build_display_name()
