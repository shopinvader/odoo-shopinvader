# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class LocomotivecmsBackend(models.Model):
    _name = 'locomotivecms.backend'
    _description = 'Locomotive CMS Backend'
    _inherit = 'connector.backend'
    _backend_type = 'locomotivecms'

    version = fields.Selection([
        ('locomotivecms_v3', 'Locomotive CMS v3'),
        ], required=True)
    location = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    lang_ids = fields.Many2many(
        'res.lang',
        string='Lang',
        required=True)


class LocomotivecmsBinding(models.AbstractModel):
    _name = 'locomotivecms.binding'
    _inherit = 'external.binding'

    backend_id = fields.Many2one(
        'locomotivecms.backend',
        string='Backend',
        required=True)
    external_id = fields.Char(string='ID on LocomotiveCMS')

    _sql_constraints = [
        ('locomotivecms_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Locomotive ID.'),
    ]
