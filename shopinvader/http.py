# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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


def convert_list(values):
    if not isinstance(values, (dict, list)):
        return values
    is_list = True
    keys = []
    res = {}
    for key, subvals in values.items():
        res[key] = convert_list(subvals)
        try:
            int(key)
        except:
            is_list = False
    if is_list:
        res = {int(k): v for k, v in res.items()}
        keys = res.keys()
        keys.sort()
        return [res[k] for k in keys]
    else:
        return res


def split_key(key):
    if '[' in key:
        return [k for k in key.replace(']', '[').split('[') if k]
    return [key]


def update_res(res, keys, value):
    key = keys[0]
    if len(keys) == 1:
        res[key] = value
    else:
        if key not in res:
            res[key] = {}
        update_res(res[key], keys[1:], value)


def convert_nested_html_form_params(params):
    """ Add the support of nested form
    vals = {
        'sale_order_line[0][qty]': u'1',
        'sale_order_line[0][id]': u'325761',
        'message': u'test de message',
        'subject_id': u'2'})

    should give with convert_nested_html_form_params(vals)

    result = {
        'message': u'my message',
        'subject_id': u'2',
        'sale_order_line': [{'id': u'325761', 'qty': u'1'}]}
    """
    res = {}
    for key, value in params.items():
        keys = split_key(key)
        update_res(res, keys, value)
    return convert_list(res)


def WrapJsonException(exception):
    """Wrapper method that modify the exception in order
    to render it like a json"""

    get_original_headers = exception.get_headers

    def get_body(environ=None):
        return json.dumps({
            'code': exception.code,
            'name': escape(exception.name),
            'description': exception.get_description(environ)
            })

    def get_headers(environ=None):
        """Get a list of headers."""
        headers = [('Content-Type', 'application/json')]
        for key, value in get_original_headers(environ=environ):
            if key != 'Content-Type':
                headers.append(key, value)
        return headers

    exception.get_body = get_body
    exception.get_headers = get_headers
    if request:
        httprequest = request.httprequest
        headers = dict(httprequest.headers)
        headers.pop('Api-Key', None)
        message = (
            'Shopinvader call url %s method %s with params %s '
            'raise the following error %s')
        args = (httprequest.url, httprequest.method, request.params, exception)
        extra = {
            'application': 'shopinvader',
            'shopinvader_url': httprequest.url,
            'shopinvader_method': httprequest.method,
            'params': request.params,
            'headers': headers,
            'status': exception.code,
            'exception_body': exception.get_body(),
            'traceback': ''.join(traceback.format_exception(*sys.exc_info())),
            }
        _logger.error(message, *args, extra=extra)
    return exception


class HttpJsonRequest(HttpRequest):
    """Http request that always return json, usefull for rest api"""

    def __init__(self, *args):
        super(HttpJsonRequest, self).__init__(*args)
        if self.httprequest.headers.get('Content-Type') == 'application/json':
            self.params = json.loads(self.httprequest.stream.read())
        elif self.params:
            self.params = convert_nested_html_form_params(self.params)

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to abitrary responses. Anything returned (except None) will
           be used as response."""
        _logger.debug('Shopinvader Handle exception %s', exception)
        if config['dev_mode']:
            raise exception
        try:
            return super(HttpRequest, self)._handle_exception(exception)
        except (UserError, ValidationError), e:
            return WrapJsonException(BadRequest(e.message or e.value))
        except MissingError, e:
            return WrapJsonException(NotFound(e.value))
        except AccessError, e:
            return WrapJsonException(Forbidden(e.value))
        except HTTPException, e:
            return WrapJsonException(e)
        except:
            return WrapJsonException(InternalServerError())

    def make_response(self, data, headers=None, cookies=None):
        data = json.dumps(data)
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'application/json'
        return super(HttpJsonRequest, self).make_response(
            data, headers=headers, cookies=cookies)


ori_get_request = Root.get_request


def get_request(self, httprequest):
    if '/shopinvader/' in httprequest.url:
        return HttpJsonRequest(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request
