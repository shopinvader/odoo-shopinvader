# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment


class CommonCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(CommonCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref('connector_locomotivecms.backend_1')

    def _get_service(self, service_class, partner):
        model_name = service_class._model_name
        session = ConnectorSession.from_env(self.env)
        env = get_environment(session, model_name, self.backend.id)
        service = env.backend.get_class(service_class, session, model_name)
        return service(env, partner)
