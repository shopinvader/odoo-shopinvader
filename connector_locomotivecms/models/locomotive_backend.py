# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class LocomotiveBackend(models.Model):
    _name = 'locomotive.backend'
    _description = 'Locomotive CMS Backend'
    _inherit = 'connector.backend'
    _backend_type = 'locomotive'

    version = fields.Selection([
        ('locomotive_v3', 'Locomotive CMS v3'),
        ], required=True)
    location = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    lang_ids = fields.Many2many(
        'res.lang',
        string='Lang',
        required=True)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env['res.company'].browse(
            self.env['res.company']._company_default_get('locomotive.backend'))
        )


class LocomotiveBinding(models.AbstractModel):
    _name = 'locomotive.binding'
    _inherit = 'external.binding'

    backend_id = fields.Many2one(
        'locomotive.backend',
        string='Backend',
        required=True)
    external_id = fields.Char(string='ID on LocomotiveCMS')

    _sql_constraints = [
        ('locomotive_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Locomotive ID.'),
    ]
