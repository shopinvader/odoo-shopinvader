# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import fields, models
import uuid


class ShopinvaderPartner(models.Model):
    _inherit = 'shopinvader.partner'

    date_initialisation = fields.Datetime(
        'Initialisation Date',
        help='date of first connection of the customer')
    date_last_reset = fields.Datetime(
        'Password reset send at',
        help='date of last password reset sent')
    nbr_reset = fields.Integer()

    def _send_reset_password_email(self, template_id, token):
        return self.env['email.template'].with_context(token=token).browse(
            template_id).send_mail(self.id)

    @job('root.shopinvader')
    def _reset_password(self, template_id, date_validity):
        self.ensure_one()
        self.write({
            'nbr_reset': (self.nbr_reset or 0) + 1,
            'date_last_reset': datetime.now(),
            })
        token = uuid.uuid4().hex
        self._send_reset_password_email(template_id, token)
        with self.backend_id.work_on(self._name) as work:
            adapter = work.component(usage='record.exporter')
            adapter.write(binding.external_id, {
                '_auth_reset_token': token,
                '_auth_reset_sent_at': date_validity,
                })
            return 'Reset Password Sent'
