# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment
from openerp.addons.shopinvader.services.sale import SaleService
from openerp.addons.shopinvader_claim.services.claim import ClaimService
from openerp.addons.shopinvader.services.address import AddressService
import json


class ShopinvaderNotification(models.Model):
    _inherit = 'shopinvader.notification'

    def _get_service(self, record, service_class):
        session = ConnectorSession.from_env(self.env)
        env = get_environment(
            session, record._name, record.shopinvader_backend_id.id)
        service = env.backend.get_class(service_class, session, record._name)
        return service(env, None, {})

    def _send(self, record):
        msg_ids = super(ShopinvaderNotification, self)._send(record)
        message = self.env['mail.mail'].browse(msg_ids)[0]
        message.external_template_key = self.template_id.external_template_key
        data = {}
        if record._name in ['sale.order', 'account.invoice']:
            if record._name == 'account.invoice':
                record = record.sale_ids[0]
            service = self._get_service(record, SaleService)
            data = {'sale': service._to_json(record)[0]}
        elif self.notification_type == 'new_customer_welcome':
            service = self._get_service(record, AddressService)
            data = {'customer': service._to_json(record)[0]}
        elif self.notification_type == 'claim_confirmation':
            service = self._get_service(record, ClaimService)
            data = {'claim': service._to_json(record)[0]}
        message.data = json.dumps(data)
        return msg_ids
