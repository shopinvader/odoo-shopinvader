# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector.connector import ConnectorUnit
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _
import logging
import functools
from collections import defaultdict

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
        return func(self, secure_params)
    return wrapped


class ShopinvaderService(ConnectorUnit):

    def __init__(self, env, partner, shopinvader_session):
        super(ShopinvaderService, self).__init__(env)
        self.partner = partner
        self.shopinvader_session = shopinvader_session
        self.cart_id = shopinvader_session.get('cart_id')

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

    def _format_error(self, errors):
        # the way we manage error are really simple
        # it will be great to have a better system
        messages = defaultdict(list)
        for key, code_error in errors.items():
            for code in code_error:
                messages[code].append(key)
        human_message = []
        for code, data in messages.items():
            if code == 'required field':
                human_message.append(
                    _('The following fields are required: %s')
                    % ', '.join(data))
            else:
                human_message.append(
                    _('The following fields are required: %s')
                    % ', '.join(data))
        return "\n".join(human_message)

    def _secure_params(self, method, params):
        if self.partner:
            partner = "%s (%s)" % (self.partner.name, self.partner.id)
        else:
            partner = "anonymous"
        _logger.debug(
            'Shopinvader call for partner %s with params %s', partner, params)
        schema = self._get_schema_for_method(method)
        v = Validator(schema, purge_unknown=True)
        if v.validate(params):
            return v.document
        _logger.error("BadRequest %s", v.errors)
        raise UserError(self._format_error(v.errors))

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
