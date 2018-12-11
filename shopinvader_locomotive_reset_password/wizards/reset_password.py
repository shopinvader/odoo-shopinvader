# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, timedelta


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
        'mail.template',
        'Mail Template',
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
        partners = self.env['shopinvader.partner'].browse(
            self._context['active_ids'])
        partners.write({'last_pwd_reset_datetime': False})
        for partner in partners:
            partner.with_delay()._reset_password(
                self.template_id.id, self.date_validity)
