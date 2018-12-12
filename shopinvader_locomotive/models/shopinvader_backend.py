# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _description = 'Locomotive CMS Backend'
    _name = 'shopinvader.backend'
    _inherit = ['shopinvader.backend', 'connector.backend', 'keychain.backend']
    _backend_name = 'locomotivecms'

    location = fields.Char(required=True, sparse='data')
    username = fields.Char(required=True, sparse='data')
    handle = fields.Char(required=True, sparse='data')
    currency_ids = fields.Many2many(
        comodel_name='res.currency',
        string='Currency')

    def synchronize_metadata(self):
        return self._export_metafields_store()

    @api.model
    def _scheduler_synchronize_currency(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).synchronize_currency()

    def synchronize_currency(self):
        return self._export_metafields_store(fields=['currency_ids'])

    def _export_metafields_store(self, fields=None):
        for record in self:
            with record.work_on(record._name) as work:
                exporter = work.component(usage='record.exporter')
                exporter.run(fields=fields)
        return True


class ChangePasswordWizard(models.TransientModel):
    """ A wizard to manage the change of users' passwords. """
    _name = "invader.change.password.wizard"
    _description = "Change Password Wizard"

    password = fields.Char(string='Password')

    def _get_backend(self):
        model = 'shopinvader.backend'
        if self._context.get('active_model') == model:
            backend = self.env[model].browse(self._context.get('active_ids'))
            return backend

    @api.multi
    def change_password_button(self):
        backend = self._get_backend()
        backend.password = self.password

    def _default_username(self):
        return self._get_backend().username

    username = fields.Char(
        string='User Login', readonly=True, default=_default_username)

