# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.connector.connector import ConnectorUnit
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.http import request
import logging
import functools

_logger = logging.getLogger(__name__)


try:
    from cerberus import Validator
except ImportError:
    _logger.debug('Can not import cerberus')


def to_int(val):
    # The javascript VM ducktape only use float and so pass float
    # to the api, the werkzeug request interpret params as unicode
    # so we have to convert params from string to float to int
    if val:
        return int(float(val))
    else:
        return None


def to_bool(val):
    if val in ('true', 'True', '1', True):
        return True
    else:
        return False


def secure_params(func):
    @functools.wraps(func)
    def wrapped(self, params):
        secure_params = self._secure_params(func.__name__, params)
        res = func(self, secure_params)
        self._log_call(func, params, secure_params, res)
        return res
    return wrapped


class ShopinvaderService(ConnectorUnit):

    def __init__(self, env, partner, shopinvader_session):
        super(ShopinvaderService, self).__init__(env)
        self.partner = partner
        self.shopinvader_session = shopinvader_session
        self.cart_id = shopinvader_session.get('cart_id')

    def _prepare_extra_log(self, func, params, secure_params, res):
        httprequest = request.httprequest
        headers = dict(httprequest.headers)
        headers.pop('Api-Key')
        return {
            'application': 'shopinvader',
            'shopinvader_url': httprequest.url,
            'shopinvader_method': httprequest.method,
            'params': params,
            'headers': headers,
            'secure_params': secure_params,
            'res': res,
            'status': 200,
        }

    def _log_call(self, func, params, secure_params, res):
        """If you want to enjoy the advanced log install the module
        logging_json"""
        if request:
            httprequest = request.httprequest
            extra = self._prepare_extra_log(func, params, secure_params, res)
            args = [httprequest.url, httprequest.method]
            message = 'Shopinvader call url %s method %s'
            _logger.debug(message, *args, extra=extra)

    def service_for(self, service_class):
        service = self.connector_env.backend.get_class(
            service_class, self.session, service_class._model_name)
        return service(
            self.connector_env, self.partner, self.shopinvader_session)

    def _get_schema_for_method(self, method):
        validator_method = '_validator_%s' % method
        if not hasattr(self, validator_method):
            raise NotImplemented
        return getattr(self, validator_method)()

    def _validate_list(self, schema, params):
        for field, vals in schema.items():
            if vals.get('type') == 'list':
                v = Validator(vals['schema'], purge_unknown=True)
                parsed = []
                for elem in params[field]:
                    if not v.validate(elem):
                        _logger.error("BadRequest %s", v.errors)
                        raise UserError(_('Invalid Form'))
                    parsed.append(v.document)
                params[field] = parsed
        return params

    def _secure_params(self, method, params):
        schema = self._get_schema_for_method(method)
        v = Validator(schema, purge_unknown=True)
        if v.validate(params):
            # TODO we should fix cerberus issue
            # https://github.com/pyeve/cerberus/issues/325
            return self._validate_list(schema, v.document)
        _logger.error("BadRequest %s", v.errors)
        raise UserError(_('Invalid Form'))

    def to_domain(self, scope):
        if not scope:
            return []
        # Convert the liquid scope syntax to the odoo domain
        OPERATORS = {
            'gt': '>',
            'gte': '>=',
            'lt': '<',
            'lte': '<=',
            'ne': '!='}
        domain = []
        if scope:
            for key, value in scope.items():
                if '.' in key:
                    key, op = key.split('.')
                    op = OPERATORS[op]
                else:
                    op = '='
                domain.append((key, op, value))
        return domain
