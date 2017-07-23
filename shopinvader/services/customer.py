# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import secure_params, ShopinvaderService
from ..backend import shopinvader
from .address import AddressService


@shopinvader
class CustomerService(ShopinvaderService):
    _model_name = 'res.partner'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def get(self, params):
        if self.partner:
            address = self.service_for(AddressService)
            customer = address._to_json(self.partner)[0]
            customer['vat'] = self.partner.vat
            return {
                'data': customer,
                'store_cache': {'customer': customer},
                }
        else:
            return {'data': {}}

    @secure_params
    def create(self, params):
        external_id = params.pop('external_id')
        if 'vat' in params:
            params['vat_subjected'] = bool(params['vat'])
        partner = self.env['res.partner'].create(params)
        self.backend_record._send_notification('new_customer_welcome', partner)
        shop_partner = self.env['shopinvader.partner'].with_context(
            connector_no_export=True).create({
                'backend_id': self.backend_record.id,
                'external_id': external_id,
                'record_id': partner.id,
                })
        address = self.service_for(AddressService)
        return {
            'data': {
                'role': shop_partner.role_id.code,
                'id': partner.id,
            },
            'store_cache': {'customer': address._to_json(partner)[0]},
        }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        address = self.service_for(AddressService)
        schema = address._validator_create()
        schema.update({
            'email': {'type': 'string', 'required': True},
            'external_id': {'type': 'string', 'required': True},
            'vat': {'type': 'string', 'required': False},
            })
        return schema

    def _validator_get(self):
        return {}
