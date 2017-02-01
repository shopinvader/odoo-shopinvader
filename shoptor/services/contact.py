# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import to_int, secure_params, ShoptorService
from openerp.addons.connector_locomotivecms.backend import locomotive
from werkzeug.exceptions import Forbidden, NotFound


@locomotive
class ContactService(ShoptorService):
    _model_name = 'res.partner'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def list(self, params):
        if not self.partner:
            return []
        else:
            return self._list(contact_type=params.get('contact_type'))

    @secure_params
    def create(self, params):
        params['parent_id'] = self.partner.id
        self.env['res.partner'].create(params)
        return self._list()

    @secure_params
    def update(self, params):
        contact = self._get_contact(params)
        contact.write(params)
        return self._list()

    @secure_params
    def delete(self, params):
        contact = self._get_contact(params)
        if self.partner == contact:
            raise Forbidden('Can not delete the partner account')
        contact.unlink()
        return self._list()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    # Validator
    def _validator_list(self):
        return {
            'contact_type': {
                'type': 'string',
                'nullable': True,
                'allowed': ['profile', 'address']},
            }

    def _validator_create(self):
        res = {
            'street': {'type': 'string', 'required': True},
            'street2': {'type': 'string', 'nullable': True},
            'zip': {'type': 'string', 'required': True},
            'city': {'type': 'string', 'required': True},
            'phone': {'type': 'string', 'nullable': True},
            'state_id': {'coerce': to_int, 'nullable': True},
            'country_id': {'coerce': to_int, 'required': True},
            'is_company': {'coerce': bool},
            }
        if 'partner_firstname' in self.env.registry._init_modules:
            res.update({
                'firstname': {
                    'type': 'string',
                    'required': True,
                    'excludes': 'name',
                    },
                'lastname': {
                    'type': 'string',
                    'required': True,
                    'excludes': 'name',
                    },
                'name': {
                    'type': 'string',
                    'required': True,
                    'excludes': ['firstname', 'lastname']},
                })
        else:
            res.update({
                'name': {'type': 'string', 'required': True},
            })
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

    def _list(self, contact_type=None):
        result = []
        if contact_type in ('profile', None):
            result += self.to_json(self.partner)
        if contact_type in ('address', None):
            result += self.to_json(self.partner.child_ids)
        return result

    def _get_contact(self, params):
        domain = [('id', '=', params['id'])]
        if self.partner.id != params['id']:
            domain.append(('parent_id', '=', self.partner.id))
        contact = self.env['res.partner'].search(domain)
        if not contact:
            raise NotFound('Not address found')
        return contact

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
            ('state_id', ['id', 'name']),
            ('country_id', ['id', 'name'])
        ]
        if 'partner_firstname' in self.env.registry._init_modules:
            res += ['firstname', 'lastname']
        return res

    def to_json(self, contact):
        return contact.jsonify(self._json_parser())
