# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, exceptions
from werkzeug.exceptions import BadRequest
from cerberus import Validator
import logging
import functools

_logger = logging.getLogger(__name__)


def to_int(val):
    # The javascript VM ducktape only use float and so pass float
    # to the api, the werkzeug request interpret params as unicode
    # so we have to convert params from string to float to int
    if val:
        return int(float(val))
    else:
        return None


def secure_params(func):
    @functools.wraps(func)
    def wrapped(self, params):
        secure_params = self._secure_params(func.__name__, params)
     	return func(self, secure_params)
    return wrapped


class ShoptorApi(models.Model):
    _name = 'shoptor.api'

    def _get_schema_for_method(self, method):
        validator_method = '_validator_%s' % method
        if not hasattr(self, validator_method):
            raise NotImplemented
        return getattr(self, validator_method)()

    def _secure_params(self, method, params):
        schema = self._get_schema_for_method(method)
        v = Validator(schema, purge_unknown=True)
        secure_params = v.normalized(params)
        if secure_params and v.validate(secure_params):
            return secure_params
        _logger.error("BadRequest %s", v.errors)
        raise BadRequest(v.errors)
