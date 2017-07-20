# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    server_type = fields.Selection([
        ('mailjet', 'Mailjet'),
        ('smtp', 'Smtp')],
        default='smtp',
        required=True)

    @api.onchange('server_type')
    def onchange_type(self):
        self.ensure_one()
        if self.server_type == 'mailjet':
            self.smtp_host = 'mailjet'
