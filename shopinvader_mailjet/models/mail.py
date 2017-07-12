# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
import json
import logging
_logger = logging.getLogger(__name__)

try:
    from mailjet_rest import Client
except ImportError, err:
    _logger.debug(err)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    data = fields.Text('Data')
    external_template_key = fields.Char()

    def _prepare_data_for_mailjet(self):
        data = json.loads(self.data) if self.data else {}
        return {
            'FromEmail': self.email_from,
            'MJ-TemplateID': self.external_template_key,
            'MJ-TemplateLanguage': True,
            'Subject': self.subject,
            'Recipients': [
                {'Email': email}
                for email in self.email_to.split(',')
                ],
            'Vars': {'store': data, 'message': self.body},
            'Attachments': [{
                'Content-type': att.file_type,
                'Filename': att.name,
                'content': att.datas,
                } for att in self.attachment_ids],
            }

    @api.multi
    def send_with_mailjet(self, auto_commit=False, raise_exception=False):
        self.ensure_one()
        auth = (self.mail_server_id.smtp_user, self.mail_server_id.smtp_pass)
        client = Client(auth=auth, version='v3')
        data = self._prepare_data_for_mailjet()
        response = client.send.create(data=data)
        if response.status_code == 200:
            self.write({
                'state': 'sent',
                'message_id': response.json()['Sent'][0]['MessageID'],
                })
        else:
            _logger.exception(
                'mailjet failed sending mail.mail %s', self.id)
            if response.reason:
                message = response.reason
            elif response.text:
                message = response.json()
            else:
                message = 'Failed to send email with mailjet'
            self.write({'state': 'exception'})
            if raise_exception:
                raise UserError(message)
        if auto_commit:
            self._cr.commit()

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        for record in self:
            if record.mail_server_id.server_type == 'mailjet':
                record.send_with_mailjet(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception)
                if auto_commit is True:
                    record._cr.commit()
            else:
                super(MailMail, record).send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception)
        return True
