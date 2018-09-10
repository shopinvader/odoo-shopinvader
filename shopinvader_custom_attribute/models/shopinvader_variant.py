# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    attributes = fields.Serialized(
        compute='_compute_attributes',
        string='Shopinvader attributes Fields')
    structured_attributes = fields.Serialized(
        compute='_compute_structured_attributes',
        string='Shopinvader attributes Fields')

    def _get_attr_vals(self, attr):
        self.ensure_one()
        if attr.attribute_type == 'select':
            return self[attr.name]['name']
        elif attr.attribute_type == 'multiselect':
            return self[attr.name].mapped('name')
        else:
            return self[attr.name]

    def _compute_attributes(self):
        for record in self:
            attributes = {}
            for group in record.attribute_set_id.attribute_group_ids:
                for attr in group.attribute_ids:
                    # all attr start with "x_" we remove it for the export
                    attributes[attr.name[2:]] = record._get_attr_vals(attr)
            record.attributes = attributes

    def _compute_structured_attributes(self):
        for record in self:
            strc_attr = []
            for group in record.attribute_set_id.attribute_group_ids:
                group_data = {
                    'group_name': group.name,
                    'fields': [],
                    }
                for attr in group.attribute_ids:
                    group_data['fields'].append({
                        'name': attr.field_description,
                        'key': attr.name[2:],
                        'value': record._get_attr_vals(attr),
                        })
                strc_attr.append(group_data)
            record.structured_attributes = strc_attr
