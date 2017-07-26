# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import secure_params, ShopinvaderService
from ..backend import shopinvader
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


@shopinvader
class RegisterAnonymousService(ShopinvaderService):
    _model_name = 'res.partner'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        sale = self.env['sale.order'].search([
            ('anonymous_token', '=', params['anonymous_token']),
            ])
        if not sale:
            raise UserError(_('Invalid Token'))
        partner = sale.partner_id
        for binding in partner.shopinvader_bind_ids:
            if self.backend_record == binding.backend_id:
                raise UserError(_('Customer already registred'))
        shop_partner = self.env['shopinvader.partner'].with_context(
            connector_no_export=True).create({
                'backend_id': self.backend_record.id,
                'external_id': params['external_id'],
                'record_id': partner.id,
                })
        return {'data': {
            'role': shop_partner.role_id.code,
            'id': partner.id,
            }}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        return {
            'anonymous_token': {'type': 'string', 'required': True},
            'external_id': {'type': 'string', 'required': True},
            }
