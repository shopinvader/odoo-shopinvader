# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job, related_action


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
    handle = fields.Char(required=True)
    lang_ids = fields.Many2many(
        'res.lang',
        string='Lang',
        required=True)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self:
            self.env['res.company']._company_default_get('locomotive.backend')
        )


class LocomotiveBinding(models.AbstractModel):
    _name = 'locomotive.binding'
    _inherit = 'external.binding'

    backend_id = fields.Many2one(
        'locomotive.backend',
        string='Backend',
        required=True)
    external_id = fields.Char(string='ID on LocomotiveCMS')

    @job(default_channel='root.shopinvader')
    @related_action(action='related_action_unwrap_binding')
    @api.multi
    def export_record(self, fields=None):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            return exporter.run(self)

    @job(default_channel='root.shopinvader')
    @related_action(action='related_action_unwrap_binding')
    @api.model
    def export_delete_record(self, backend, external_id):
        with backend.work_on(self._name) as work:
            deleter = work.component(usage='record.exporter.deleter')
            return deleter.run(external_id)

    _sql_constraints = [
        ('locomotive_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Locomotive ID.'),
    ]
