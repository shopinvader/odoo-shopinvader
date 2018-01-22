# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
from datetime import datetime
from decorator import decorator
from odoo.http import Controller, request
from odoo.http import HttpRequest, Root
from odoo.tools import config
from werkzeug.exceptions import HTTPException
from werkzeug.utils import escape
from odoo.exceptions import (
    Warning as UserError, MissingError, AccessError, ValidationError)
from werkzeug.exceptions import (
    BadRequest, NotFound, Forbidden, InternalServerError)
from odoo.http import request
import sys
import traceback
import json
import logging

_logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)


def WrapJsonException(exception):
    """Wrapper method that modify the exception in order
    to render it like a json"""

    get_original_headers = exception.get_headers

    def get_body(environ=None):
        return JSONEncoder().encode({
            'code': exception.code,
            'name': escape(exception.name),
            'description': exception.get_description(environ)
            })

    def get_headers(environ=None):
        """Get a list of headers."""
        _headers = [('Content-Type', 'application/json')]
        for key, value in get_original_headers(environ=environ):
            if key != 'Content-Type':
                _headers.append(key, value)
        return _headers

    exception.get_body = get_body
    exception.get_headers = get_headers
    if request:
        httprequest = request.httprequest
        headers = dict(httprequest.headers)
        headers.pop('Api-Key', None)
        message = (
            'RESTFULL call to url %s with method %s and params %s '
            'raise the following error %s')
        args = (httprequest.url, httprequest.method, request.params, exception)
        extra = {
            'application': request.backend.name,
            'url': httprequest.url,
            'method': httprequest.method,
            'params': request.params,
            'headers': headers,
            'status': exception.code,
            'exception_body': exception.get_body(),
            'traceback': ''.join(traceback.format_exception(*sys.exc_info())),
            }
        _logger.error(message, *args, extra=extra)
    return exception


def handle_exception_as_json(func):
    def inner(func, self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (UserError, ValidationError), e:
            return WrapJsonException(
                BadRequest(e.message or e.value or e.name))
        except MissingError, e:
            return WrapJsonException(NotFound(e.value))
        except AccessError, e:
            return WrapJsonException(Forbidden(e.value))
        except HTTPException, e:
            return WrapJsonException(e)
        except:
            return WrapJsonException(InternalServerError())
    return decorator(inner, func)


class InvaderController(Controller):

    def _get_component_context(self):
        """
        This method can be inherited to add parameter into the component
        context
        :return: dict of key value.
        """
        return {}

    @handle_exception_as_json
    def send_to_service(self, service_name, params):
        with request.backend.work_on(
                model_name=request.backend._name,
                **self._get_component_context()
        ) as work:
            service = work.component(usage=service_name)
            start = datetime.now()
            method = request.httprequest.method
            if method == 'GET':
                res = service.get(params)
            elif method == 'POST':
                res = service.create(params)
            elif method == 'PUT':
                res = service.update(params)
            elif method == 'DELETE':
                res = service.delete(params)
            res = self.make_json_response(res)
            _logger.info('Invader Response in %s', datetime.now() - start)
            return res

    def make_json_response(self, data, headers=None, cookies=None):
        data = JSONEncoder().encode(data)
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'application/json'
        return request.make_response(data, headers=headers, cookies=cookies)
