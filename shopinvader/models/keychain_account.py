# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class KeychainAccount(models.Model):

    _inherit = 'keychain.account'

    @classmethod
    def _encode_password(cls, data, env):
        if env.registry.in_test_mode():
            return data
        return super(KeychainAccount, cls)._encode_password(data, env)

    @api.multi
    def get_password(self):
        self.ensure_one()
        if self.env.registry.in_test_mode():
            return self.password
        return super(KeychainAccount, self).get_password()
