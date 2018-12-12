# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class LeadService(Component):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.lead.service'
    _usage = 'lead'
    _expose_model = 'crm.lead'

    # The following methods are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    def create(self, **params):
        vals = self._prepare_lead(params)
        lead = self.env['crm.lead'].create(vals)
        self.shopinvader_backend._send_notification('lead_confirmation', lead)
        return {}

    # The following methods are 'private' and should be never NEVER be called
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        res = {
            'email': {'type': 'string', 'required': True},
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
            ('email', 'email_from'),
        ]
        for human_key, key in map_key:
            if human_key in params:
                params[key] = params.pop(human_key)
        params['shopinvader_backend_id'] = self.shopinvader_backend.id
        return params
