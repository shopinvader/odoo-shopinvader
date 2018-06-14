# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo.addons.component.core import Component


_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    # Response validator
    def _common_response_schema(self):
        schema = super(CartService, self)._common_response_schema()
        payment_schema = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'amount': {
                    'type': 'float',
                },
                'available_methods': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'count': {
                            'type': 'integer',
                            'required': True,
                        },
                        'items': {
                            'type': 'list',
                            'required': True,
                            'schema': {
                                'type': 'dict',
                                'nullable': True,
                                'schema': {
                                    'code': {
                                        'type': ['string', 'boolean'],
                                        'required': True,
                                    },
                                    'description': {
                                        'type': ['boolean', 'string'],
                                        'required': True,
                                    },
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
                        },
                    },
                },
                'selected_method': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'code': {
                            'type': ['boolean', 'string'],
                            'required': True,
                        },
                        'description': {
                            'type': ['boolean', 'string'],
                            'required': True,
                        },
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
            },
        }
        notifications_schema = {
            'type': 'list',
            'nullable': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'message': {
                        'type': 'string',
                        'required': True,
                    },
                    'type': {
                        'type': 'string',
                    },
                },
            },
        }
        # Update schema
        schema.get('data', {}).get('schema', {}).update({
            'payment': payment_schema,
        })
        schema.get('store_cache', {}).get('schema', {}).update({
            'notifications': notifications_schema,
        })
        schema.update({
            'redirect_to': {
                'type': 'string',
                'nullable': True,
            },
        })
        return schema

    @property
    def _add_payment_response_schema(self):
        return self._common_response_schema()

    @property
    def _check_payment_response_schema(self):
        return self._common_response_schema()
