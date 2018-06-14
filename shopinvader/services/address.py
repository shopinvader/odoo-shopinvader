# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError
from odoo import _


class AddressService(Component):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.address.service'
    _usage = 'addresses'
    _expose_model = 'res.partner'

    # The following method are 'public' and can be called from the controller.

    def get(self, _id):
        return self._to_json(self._get(_id))

    def search(self, **params):
        if not self.partner:
            return {'data': []}
        else:
            return self._paginate_search(**params)

    def create(self, **params):
        params['parent_id'] = self.partner.id
        if not params.get('type'):
            params['type'] = 'other'
        self.env['res.partner'].create(self._prepare_params(params))
        return self.search()

    def update(self, _id, **params):
        address = self._get(_id)
        address.write(self._prepare_params(params, update=True))
        res = self.search()
        if address.address_type == 'profile':
            res['store_cache'] = {'customer': self._to_json(address)[0]}
        return res

    def delete(self, _id):
        address = self._get(_id)
        if self.partner == address:
            raise AccessError(_('Can not delete the partner account'))
        address.active = False
        return self.search()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    # Validator
    @property
    def _search_request_schema(self):
        return {
            'scope': {
                'type': 'dict',
                'nullable': True,
                },
            }

    @property
    def _create_request_schema(self):
        res = {
            'street': {'type': 'string', 'required': True, 'empty': False},
            'street2': {'type': 'string', 'nullable': True},
            'zip': {'type': 'string', 'required': True, 'empty': False},
            'city': {'type': 'string', 'required': True, 'empty': False},
            'phone': {'type': 'string', 'nullable': True, 'empty': False},
            'state': {
                'type': 'dict',
                'schema': {
                    'id': {
                        'coerce': to_int,
                        'nullable': True},
                    }
                },
            'country': {
                'type': 'dict',
                'schema': {
                    'id': {
                        'coerce': to_int,
                        'required': True,
                        'nullable': False},
                    }
                },
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

    @property
    def _update_request_schema(self):
        res = self._create_request_schema
        for key in res:
            if 'required' in res[key]:
                del res[key]['required']
        return res

    @property
    def _delete_request_schema(self):
        return {}

    # Response validator
    def _common_response_schema(self):
        schema = {
            'size': {
                'type': 'integer',
                'min': 0,
            },
            'data': {
                'type': 'list',
                'required': True,
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'id': {
                            'type': 'integer',
                            'required': True,
                        },
                        'display_name': {
                            'type': 'string',
                            'required': True,
                        },
                        'name': {
                            'type': 'string',
                            'required': True,
                        },
                        'ref': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'street': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'street2': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'zip': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'city': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'phone': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'opt_in': {
                            'type': 'boolean',
                        },
                        'opt_out': {
                            'type': 'boolean',
                        },
                        'vat': {
                            'type': 'string',
                            'nullable': True,
                        },
                        'state': {
                            'type': 'dict',
                            'nullable': True,
                            'schema': {
                                'id': {
                                    'type': 'integer',
                                    'required': True,
                                },
                                'name': {
                                    'type': 'string',
                                    'required': True,
                                },
                            },
                        },
                        'country': {
                            'type': 'dict',
                            'nullable': True,
                            'schema': {
                                'id': {
                                    'type': 'integer',
                                    'required': True,
                                },
                                'name': {
                                    'type': 'string',
                                    'required': True,
                                },
                            },
                        },
                        'address_type': {
                            'type': 'string',
                        },
                        'is_company': {
                            'type': 'boolean',
                        },
                    },
                },
            }
        }
        return schema

    @property
    def _create_response_schema(self):
        return self._common_response_schema()

    @property
    def _update_response_schema(self):
        return self._common_response_schema()

    @property
    def _search_response_schema(self):
        return self._common_response_schema()

    def _get_base_search_domain(self):
        return [('id', 'child_of', self.partner.id)]

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
            'vat',
            ('state_id:state', ['id', 'name']),
            ('country_id:country', ['id', 'name']),
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

    def _prepare_params(self, params, update=False):
        for key in ['country', 'state']:
            if key in params:
                val = params.pop(key)
                if val.get('id'):
                    params["%s_id" % key] = val['id']
        return params
