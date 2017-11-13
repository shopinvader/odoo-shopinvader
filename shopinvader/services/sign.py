# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from .helper import secure_params
from odoo.exceptions import UserError
import logging
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)


class SignService(Component):
    _inherit = ['shopinvader.service', 'base.locomotive.connector']
    _name = 'shopinvader.sign.service'
    _usage = 'sign.service'

    @secure_params
    def get(self, params):
        return self._assign_cart_and_get_store_cache()

    @secure_params
    def update(self, params):
        sale = self.env['sale.order'].search([
            ('anonymous_token', '=', params['anonymous_token']),
            ])
        if not sale:
            raise UserError(_('invalid token'))
        for binding in sale.partner_id.shopinvader_bind_ids:
            if self.collection == binding.backend_id:
                raise UserError(_('customer already registred'))
        self.work.partner = sale.partner_id
        return self._create_shopinvader_binding(params['external_id'])

    @secure_params
    def create(self, params):
        external_id = params.pop('external_id')
        if 'vat' in params:
            params['vat_subjected'] = bool(params['vat'])
            params['is_company'] = True
        self.work.partner = self.env['res.partner'].create(params)
        self.collection._send_notification(
            'new_customer_welcome', self.partner)
        return self._create_shopinvader_binding(external_id)

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_get(self):
        return {}

    def _validator_create(self):
        address = self.component(usage='address.service')
        schema = address._validator_create()
        schema.update({
            'email': {
                'type': 'string',
                'required': True,
                },
            'external_id': {
                'type': 'string',
                'required': True,
                },
            'vat': {
                'type': 'string',
                'required': False,
                },
            })
        return schema

    def _validator_update(self):
        return {
            'external_id': {
                'type': 'string',
                'required': True,
                },
            'anonymous_token': {
                'type': 'string',
                'required': True,
                },
            }

    def _get_and_assign_cart(self):
        cart_service = self.component(usage='cart.service')
        cart = cart_service._get()
        if cart:
            if self.partner and cart.partner_id != self.partner:
                # we need to affect the cart to the partner
                cart.write_with_onchange({
                    'partner_id': self.partner.id,
                    'partner_shipping_id': self.partner.id,
                    'partner_invoice_id': self.partner.id,
                    })
            return cart_service._to_json(cart)['data']
        else:
            return {}

    def _assign_cart_and_get_store_cache(self):
        address = self.component(usage='address.service')
        return {
            'store_cache': {
                'cart': self._get_and_assign_cart(),
                'customer': address._to_json(self.partner)[0],
                }
            }

    def _create_shopinvader_binding(self, external_id):
        shop_partner = self.env['shopinvader.partner'].with_context(
            connector_no_export=True).create({
                'backend_id': self.collection.id,
                'external_id': external_id,
                'record_id': self.partner.id,
                })
        response = self._assign_cart_and_get_store_cache()
        response['data'] = {
            'role': shop_partner.role_id.code,
            'id': self.partner.id,
        }
        return response
