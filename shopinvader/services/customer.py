# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import secure_params, ShoptorService
from openerp.addons.connector_locomotivecms.backend import locomotive
from .contact import ContactService


@locomotive
class CustomerService(ShoptorService):
    _model_name = 'res.partner'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        external_id = params.pop('external_id')
        partner = self.env['res.partner'].create(params)
        self.env['locomotive.partner'].with_context(
            connector_no_export=True).create({
                'backend_id': self.backend_record.id,
                'external_id': external_id,
                'record_id': partner.id,
                })
        return {'id': partner.id}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_create(self):
        contact = self.service_for(ContactService)
        schema = contact._validator_create()
        schema.update({
            'email': {'type': 'string', 'required': True},
            'external_id': {'type': 'string', 'required': True},
            })
        return schema
