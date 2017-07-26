# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import to_int, secure_params, ShopinvaderService
from ..backend import shopinvader
from werkzeug.exceptions import Forbidden, NotFound


@shopinvader
class AddressService(ShopinvaderService):
    _model_name = 'res.partner'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def get(self, params):
        if not self.partner:
            return []
        else:
            return self._list(params.pop('domain', None))

    @secure_params
    def create(self, params):
        params['parent_id'] = self.partner.id
        self.env['res.partner'].create(params)
        return self._list()

    @secure_params
    def update(self, params):
        address = self._get_address(params)
        address.write(params)
        res = self._list()
        if address.address_type == 'profile':
            res['store_cache'] = {'customer': self._to_json(address)[0]}
        return res

    @secure_params
    def delete(self, params):
        address = self._get_address(params)
        if self.partner == address:
            raise Forbidden('Can not delete the partner account')
        address.unlink()
        return self._list()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    # Validator
    def _validator_get(self):
        return {
            'domain': {
                'coerce': self.to_domain,
                'nullable': True,
                },
            }

    def _validator_create(self):
        res = {
            'street': {'type': 'string', 'required': True, 'empty': False},
            'street2': {'type': 'string', 'nullable': True},
            'zip': {'type': 'string', 'required': True, 'empty': False},
            'city': {'type': 'string', 'required': True, 'empty': False},
            'phone': {'type': 'string', 'nullable': True, 'empty': False},
            'state_id': {'coerce': to_int, 'nullable': True},
            'country_id': {
                'coerce': to_int,
                'required': True,
                'nullable': False},
            'is_company': {'coerce': bool},
            'opt_in': {'coerce': bool},
            'opt_out': {'coerce': bool},
            }
        if 'partner_firstname' in self.env.registry._init_modules:
            res.update({
                'firstname': {
                    'type': 'string',
                    'required': True,
                    'excludes': 'name',
                    'empty': False
                    },
                'lastname': {
                    'type': 'string',
                    'required': True,
                    'excludes': 'name',
                    'empty': False
                    },
                'name': {
                    'type': 'string',
                    'required': True,
                    'excludes': ['firstname', 'lastname'],
                    'empty': False,
                    },
                })
        else:
            res.update({
                'name': {'type': 'string', 'required': True},
            })
        if 'company' in self.env['res.partner']._fields:
            res.update({'company': {'type': 'string'}})
        return res

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if 'required' in res[key]:
                del res[key]['required']
        res.update({'id': {'coerce': to_int, 'required': True}})
        return res

    def _validator_delete(self):
        return {
            'id': {'coerce': to_int, 'required': True},
            }

    def _list(self, domain=None):
        if not domain:
            domain = []
        domain = [('id', 'child_of', self.partner.id)] + domain
        partners = self.env['res.partner'].search(domain)
        return {'data': self._to_json(partners)}

    def _get_address(self, params):
        domain = [('id', '=', params['id'])]
        if self.partner.id != params['id']:
            domain.append(('parent_id', '=', self.partner.id))
        address = self.env['res.partner'].search(domain)
        if not address:
            raise NotFound('Not address found')
        return address

    def _json_parser(self):
        res = [
            'id',
            'display_name',
            'name',
            'ref',
            'street',
            'street2',
            'zip',
            'city',
            'phone',
            'opt_in',
            'opt_out',
            ('state_id', ['id', 'name']),
            ('country_id', ['id', 'name']),
            'address_type',
            'is_company',
        ]
        if 'partner_firstname' in self.env.registry._init_modules:
            res += ['firstname', 'lastname']
        if 'company' in self.env['res.partner']._fields:
            res.append('company')
        return res

    def _to_json(self, address):
        return address.jsonify(self._json_parser())
