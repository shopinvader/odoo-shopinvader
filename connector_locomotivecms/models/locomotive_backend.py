# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LocomotiveBackend(models.Model):
    _name = 'locomotive.backend'
    _description = 'Locomotive CMS Backend'
    _inherit = ['connector.backend', 'keychain.backend']
    _backend_name = 'locomotivecms'

    @api.model
    def _default_company_id(self):
        return self.env['res.company']._company_default_get(
            'locomotive.backend')

    location = fields.Char(required=True, sparse='data')
    username = fields.Char(required=True, sparse='data')
    handle = fields.Char(required=True, sparse='data')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=_default_company_id)
