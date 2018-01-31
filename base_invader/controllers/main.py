# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from contextlib import contextmanager

from odoo.http import Controller
from odoo.http import Response
from odoo.http import request
from odoo.http import route
from werkzeug.exceptions import BadRequest

_logger = logging.getLogger(__name__)


ROOT_PATH = '/invader/'


class InvaderController(Controller):

    def _get_component_context(self):
        """
        This method can be inherited to add parameter into the component
        context
        :return: dict of key value.
        """
        return {}

    def make_response(self, data):
        if isinstance(data, Response):
            # The response has been build by the called method...
            return data
        # By default return result as json
        return request.make_json_response(data)

    @contextmanager
    def service_component(self, service_name):
        """
        Return the component that implements the methods of the requested
        service.
        :param service_name:
        :return: an instance of invader.service component
        """
        with request.backend.work_on(
            request.backend._name,
            **self._get_component_context()
        ) as work:
            service = work.component(usage=service_name)
            yield service

    @route([
        ROOT_PATH + '<string:_service_name>/',
        ROOT_PATH + '<string:_service_name>/search',
        ROOT_PATH + '<string:_service_name>/<int:_id>/',
        ROOT_PATH + '<string:_service_name>/<int:_id>/get'
    ], methods=['GET'], auth="api_key", csrf=False)
    def get(self, _service_name, _id=None, **params):
        with self.service_component(_service_name) as service:
            method_name = 'get' if _id else 'search'
            res = service.dispatch(method_name, _id, params)
            return self.make_response(res)

    @route([
        ROOT_PATH + '<string:_service_name>/',
        ROOT_PATH + '<string:_service_name>/<string:method_name>',
        ROOT_PATH + '<string:_service_name>/<int:_id>/',
        ROOT_PATH + '<string:_service_name>/<int:_id>/<string:method_name>'
    ], methods=['POST', 'PUT'], auth="api_key", csrf=False)
    def modify(self, _service_name, _id=None, method_name=None, **params):
        if not method_name:
            method_name = 'update' if _id else 'create'
        if method_name.startswith('_'):
            _logger.error("Invader service called with an unallowed method "
                          "name: %s.\n Method can't start with '_'",
                          method_name)
            raise BadRequest()
        with self.service_component(_service_name) as service:
            res = service.dispatch(method_name, _id, params)
            return self.make_response(res)

    @route([
        ROOT_PATH + '<string:_service_name>/<int:_id>/',
    ], methods=['DELETE'], auth="api_key", csrf=False)
    def delete(self, _service_name, _id):
        with self.service_component(_service_name) as service:
            res = service.dispatch('delete', _id)
            return self.make_response(res)
