# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models
from .tools import sanitize_attr_name


class ProductFilter(models.Model):
    _name = 'product.filter'
    _description = 'Product Filter'
    _order = 'sequence,name'

    sequence = fields.Integer()
    based_on = fields.Selection(
        selection=[
            ('field', 'Field'),
            ('variant_attribute', 'Variant Attribute')
        ],
        required=True
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        'Field',
        domain=[('model', 'in', (
            'product.template',
            'product.product',
            'shopinvader.product',
            ))])
    attribute_id = fields.Many2one(
        string='Attribute',
        comodel_name='product.attribute'
    )
    help = fields.Html(translate=True)
    name = fields.Char(translate=True, required=True)
    display_name = fields.Char(
        compute="_compute_display_name"
    )

    def _compute_display_name(self):
        for pfilter in self:
            if pfilter.based_on == 'field':
                pfilter.display_name = pfilter.field_id.name
            else:
                pfilter.display_name = 'variant_attributes.%s'\
                    % sanitize_attr_name(pfilter.attribute_id)
