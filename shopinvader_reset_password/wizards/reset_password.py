# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.queue.job import job
from datetime import datetime, timedelta
from openerp.addons.connector_locomotivecms.connector import get_environment
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter


@job
def reset_password(session, model_name, binding_id, template_id,
                   date_validity):
    binding = session.env[model_name].browse(binding_id)
    token = binding._reset_password(template_id, date_validity)
    env = get_environment(session, model_name, binding.backend_id.id)
    adapter = env.get_connector_unit(CRUDAdapter)
    adapter.write(binding.external_id, {
        '_auth_reset_token': token,
        '_auth_reset_sent_at': date_validity,
        })
    return 'Reset Password Sent'


class ShopinvaderResetPassword(models.TransientModel):
    _name = 'shopinvader.reset.password'
    _description = 'Shopinvader Reset Password'

    delay = fields.Selection([
        ('manually', 'Manually'),
        ('6-hours', '6 Hours'),
        ('2-days', '2-days'),
        ('7-days', '7 Days'),
        ('14-days', '14 Days'),
        ], default='6-hours',
        required=True,
        )
    template_id = fields.Many2one(
        'email.template',
        'Email Template',
        required=True,
        domain=[('model_id', '=', 'shopinvader.partner')])
    date_validity = fields.Datetime('Date Validity')

    @api.onchange('delay')
    def onchange_delay(self):
        if self.delay != 'manually':
            duration, key = self.delay.split('-')
            kwargs = {key: float(duration)}
            self.date_validity = datetime.now() + timedelta(**kwargs)

    @api.model
    def create(self, vals):
        record = super(ShopinvaderResetPassword, self).create(vals)
        record.onchange_delay()
        return record

    @api.multi
    def confirm(self):
        self.ensure_one()
        self.env['shopinvader.partner'].write({'date_initialisation': False})
        for partner_id in self._context['active_ids']:
            session = ConnectorSession.from_env(self.env)
            reset_password.delay(
                session, 'shopinvader.partner', partner_id,
                self.template_id.id, self.date_validity)
