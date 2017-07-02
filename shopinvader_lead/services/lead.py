# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.shopinvader.services.helper import (
    secure_params, ShopinvaderService, to_int)
from openerp.addons.shopinvader.backend import shopinvader


@shopinvader
class LeadService(ShopinvaderService):
    _model_name = 'crm.lead'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        vals = self._prepare_lead(params)
        self.env['crm.lead'].create(vals)
        return {}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        res = {
            'name': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': True},
            'company': {'type': 'string', 'required': True},
            'street': {'type': 'string', 'required': False},
            'street2': {'type': 'string', 'nullable': True},
            'zip': {'type': 'string', 'required': True},
            'city': {'type': 'string', 'required': True},
            'phone': {'type': 'string', 'nullable': True},
            'mobile': {'type': 'string', 'nullable': True},
            'state_id': {'coerce': to_int, 'nullable': True},
            'country_id': {'coerce': to_int, 'required': True},
            }

        if 'crm_lead_firstname' in self.env.registry._init_modules:
            res.update({
                'contact_firstname': {'type': 'string', 'required': True},
                'contact_lastname': {'type': 'string', 'required': True},
                })
        else:
            res['contact_name'] = {'type': 'string', 'required': True}
        return res

    def _prepare_lead(self, params):
        map_key = [
            ('contact_firstname', 'contact_name'),
            ('company', 'partner_name'),
        ]
        for human_key, key in map_key:
            if human_key in params:
                params[key] = params.pop(human_key)
        return params
