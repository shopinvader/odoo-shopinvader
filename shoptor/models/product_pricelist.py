# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class LocomotivecmspPricelist(models.Model):
    _name = 'locomotivecms.pricelist'
    _description = 'Locomotivecms Pricelist'

    backend_id = fields.Many2one(
        'locomotivecms.backend',
        'Backend')
    record_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        domain=[('type', '=', 'sale')])
    tax_included = fields.Boolean()
    code = fields.Char(required=True)

    _sql_constraints = [
        ('pricelist_uniq', 'unique(backend_id, record_id, tax_included)',
         'Pricelist with the option tax included must be uniq per backend.'),
        ('code_uniq', 'unique(backend_id, code)',
         'Code must be uniq per backend.'),
    ]
