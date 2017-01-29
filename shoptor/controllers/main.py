# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from openerp import http
from openerp.http import request
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment


def rjson(result):
    return request.make_response(
        json.dumps(result),
        headers={'Content-Type': 'application/json'})


class ShoptorController(http.Controller):

    def _get_service(self, service):
        model_name = service._model_name
        session = ConnectorSession.from_env(request.env)
        env = get_environment(session, model_name, request.backend_id)
        return env.get_connector_unit(service)
