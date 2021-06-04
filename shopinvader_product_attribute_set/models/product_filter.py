# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductFilter(models.Model):
    _inherit = "product.filter"

    based_on = fields.Selection(
        selection_add=[("product_attribute", "Product Attribute")]
    )
    product_attribute_id = fields.Many2one(
        string="Product Attribute", comodel_name="attribute.attribute"
    )

    def _build_display_name(self):
        if self.based_on == "product_attribute":
            return "attributes.%s" % self.product_attribute_id.export_name
        else:
            return super(ProductFilter, self)._build_display_name()
