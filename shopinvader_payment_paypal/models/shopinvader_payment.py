# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

try:
    from paypalrestsdk import Api, WebProfile
except (ImportError, IOError) as err:
    _logger.debug(err)


class ShopinvaderPayment(models.Model):

    _inherit = 'shopinvader.payment'

    paypal_profile_id = fields.Char(
        help="Identifier of the paypal profile used to customize the Paypal"
             "screen",
        readonly=True
    )

    paypal_profile_info = fields.Text(
        help="Profile informations used to customize the Paypal screen",
        compute="_compute_paypal_profile_info",
        inverse="_inverse_paypal_profile_info"
    )

    def _get_paypal_api(self):
        keychain = self.env['keychain.account']
        account = keychain.sudo().retrieve([
            ('namespace', '=', 'paypal')
        ])
        if account:
            account = account[0]
        else:
            return False
        params = account.get_data()
        params['client_secret'] = account._get_password()
        return Api(params)

    @api.multi
    def _compute_paypal_profile_info(self):
        paypal = self._get_paypal_api()
        for record in self.filtered(lambda a: a.paypal_profile_id):
            web_profile = WebProfile.find(record.paypal_profile_id, api=paypal)
            record.paypal_profile_info = json.dumps(web_profile.to_dict())

    @api.multi
    def _inverse_paypal_profile_info(self):
        paypal = self._get_paypal_api()
        for record in self:
            if not record.paypal_profile_info:
                continue
            info = json.loads(record.paypal_profile_info)
            if record.paypal_profile_id:
                web_profile = WebProfile.find(
                    record.paypal_profile_id, api=paypal)
                if not web_profile.update(info):
                    raise UserError(_('Error updating paypal profile:\n %s') %
                                    web_profile.error)
            else:
                web_profile = WebProfile(info, api=paypal)
                if not web_profile.create():
                    raise UserError(_('Error creating paypal profile:\n %s') %
                                    web_profile.error)
                record.paypal_profile_id = web_profile.id
