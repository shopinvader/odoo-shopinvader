# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangePasswordWizard(models.TransientModel):
    """Wizard to change the locomotiveCMS passwords"""
    _name = "invader.change.password.wizard"
    _description = "Change Locomotive Password Wizard"

    def _get_backend(self):
        """Retrieve shopinvader.backend from context"""
        model = 'shopinvader.backend'
        if self._context.get('active_model') == model:
            backend = self.env[model].browse(self._context.get('active_ids'))
            return backend

    def _default_username(self):
        """Fetch username from backend"""
        return self._get_backend().username

    username = fields.Char(
        string='User Login', readonly=True, default=_default_username)

    password = fields.Char(string='Password')

    @api.multi
    def change_password_button(self):
        """Persist new password."""
        self.ensure_one()
        if self.password:
            self._get_backend() = self.password
        self.password = ""
