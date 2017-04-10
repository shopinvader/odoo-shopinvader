# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.http import HttpRequest, Root
from werkzeug.exceptions import HTTPException
from werkzeug.utils import escape
from openerp.exceptions import Warning as UserError, MissingError, AccessError
from werkzeug.exceptions import (
    BadRequest, NotFound, Forbidden, InternalServerError)
import json


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
    return exception


class HttpJsonRequest(HttpRequest):
    """Http request that always return json, usefull for rest api"""

    def __init__(self, *args):
        super(HttpJsonRequest, self).__init__(*args)
        if self.httprequest.headers.get('Content-Type') == 'application/json':
            self.params = json.loads(self.httprequest.stream.read())

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to abitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return super(HttpRequest, self)._handle_exception(exception)
        except UserError, e:
            return WrapJsonException(BadRequest(e.message))
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
    if 'shoptor' in httprequest.url:
        return HttpJsonRequest(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request
