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
        contact_type = params.get('contact_type')
        partner = self._get_partner(params['partner_email'])
        result = []
        if contact_type in ('profile', None):
            result += self.to_json(partner)
        if contact_type in ('address', None):
            result += self.to_json(partner.child_ids)
        return result

    @secure_params
    def create(self, params):
        partner = self._get_partner(params['partner_email'])
        params['parent_id'] = partner.id
        params.pop('partner_email')
        contact = self.env['res.partner'].create(params)
        return self.to_json(contact)[0]

    @secure_params
    def update(self, params):
        contact = self._get_contact(params)
        params.pop('partner_email')
        contact.write(params)
        return self.to_json(contact)[0]

    @secure_params
    def delete(self, params):
        partner = self._get_partner(params['partner_email'])
        contact = self._get_contact(params)
        if partner == contact:
            raise Forbidden('Can not delete the partner account')
        contact.unlink()
        return True

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    # Validator
    def _validator_list(self):
        return {
            'partner_email': {'type': 'string', 'required': True},
            'contact_type': {
                'type': 'string',
                'nullable': True,
                'allowed': ['profile', 'address']},
            }

    def _validator_create(self):
        res = {
            'partner_email': {'type': 'string', 'required': True},
            'name': {'type': 'string'},
            'street': {'type': 'string'},
            'street2': {'type': 'string'},
            'zip': {'type': 'string'},
            'city': {'type': 'string'},
            'phone': {'type': 'string'},
            'state_id': {'coerce': to_int},
            'country_id': {'coerce': to_int},
            }
        if 'partner_firstname' in self.env.registry._init_modules:
            res.update({
                'firstname': {'type': 'string'},
                'lastname': {'type': 'string'},
                })
        return res

    def _validator_update(self):
        res = self._validator_create()
        res.update({'id': {'coerce': to_int, 'required': True}})
        return res

    def _validator_delete(self):
        return {
            'partner_email': {'type': 'string', 'required': True},
            'id': {'coerce': to_int, 'required': True},
            }

    def _get_contact(self, params):
        partner = self._get_partner(params['partner_email'])
        domain = [('id', '=', params['id'])]
        if partner.id != params['id']:
            domain.append(('parent_id', '=', partner.id))
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
            ('state_id', ['name']),
            ('country_id', ['name'])
        ]
        if 'partner_firstname' in self.env.registry._init_modules:
            res += ['firstname', 'lastname']
        return res

    def to_json(self, contact):
        return contact.jsonify(self._json_parser())
