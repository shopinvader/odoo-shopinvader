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

    def _validate_method_name(self, method_name):
        if method_name.startswith('_'):
            _logger.error("Invader service called with an unallowed method "
                          "name: %s.\n Method can't start with '_'",
                          method_name)
            raise BadRequest()
        return True

    def _process_method(self, service_name, method_name, _id=None,
                        params=None):
        self._validate_method_name(method_name)
        with self.service_component(service_name) as service:
            res = service.dispatch(method_name, _id, params)
            return self.make_response(res)

    @route([
        ROOT_PATH + '<string:_service_name>',
        ROOT_PATH + '<string:_service_name>/search',
        ROOT_PATH + '<string:_service_name>/<int:_id>',
        ROOT_PATH + '<string:_service_name>/<int:_id>/get'
    ], methods=['GET'], auth="api_key", csrf=False)
    def get(self, _service_name, _id=None, **params):
        method_name = 'get' if _id else 'search'
        return self._process_method(_service_name, method_name, _id, params)

    @route([
        ROOT_PATH + '<string:_service_name>',
        ROOT_PATH + '<string:_service_name>/<string:method_name>',
        ROOT_PATH + '<string:_service_name>/<int:_id>',
        ROOT_PATH + '<string:_service_name>/<int:_id>/<string:method_name>'
    ], methods=['POST'], auth="api_key", csrf=False)
    def modify(self, _service_name, _id=None, method_name=None, **params):
        if not method_name:
            method_name = 'update' if _id else 'create'
        return self._process_method(_service_name, method_name, _id, params)

    @route([
        ROOT_PATH + '<string:_service_name>/<int:_id>',
    ], methods=['PUT'], auth="api_key", csrf=False)
    def update(self, _service_name, _id, **params):
        return self._process_method(_service_name, 'update', _id, params)

    @route([
        ROOT_PATH + '<string:_service_name>/<int:_id>',
    ], methods=['DELETE'], auth="api_key", csrf=False)
    def delete(self, _service_name, _id):
        return self._process_method(_service_name, 'delete', _id)
