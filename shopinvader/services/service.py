# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import UserError, MissingError
from odoo import _


class BaseShopinvaderService(AbstractComponent):
    _inherit = 'base.rest.service'
    _name = 'base.shopinvader.service'
    _collection = 'locomotive.backend'
    _expose_model = None

    @property
    def partner(self):
        return self.work.partner

    @property
    def shopinvader_session(self):
        return self.work.shopinvader_session

    @property
    def locomotive_backend(self):
        return self.work.locomotive_backend

    def _scope_to_domain(self, scope):
        # Convert the liquid scope syntax to the odoo domain
        try:
            OPERATORS = {
                'gt': '>',
                'gte': '>=',
                'lt': '<',
                'lte': '<=',
                'ne': '!='}
            domain = []
            for key, value in scope.items():
                if '.' in key:
                    key, op = key.split('.')
                    op = OPERATORS[op]
                else:
                    op = '='
                domain.append((key, op, value))
            return domain
        except Exception, e:
            raise UserError(_('Invalid scope %s, error : %s'), scope, e)

    def _paginate_search(
            self,  default_page=1, default_per_page=5, **params):
        domain = self._get_base_search_domain()
        if params.get('scope'):
            domain += self._scope_to_domain(params['scope'])
        if params.get('domain'):
            domain += params['domain']
        model_obj = self.env[self._expose_model]
        total_count = model_obj.search_count(domain)
        page = params.get('page', default_page)
        per_page = params.get('per_page', default_per_page)
        records = model_obj.search(
            domain, limit=per_page, offset=per_page*(page-1))
        return {
            'size': total_count,
            'data': self._to_json(records),
            }

    def _get(self,  _id):
        domain = self._get_base_search_domain()
        domain.append(('id', '=', _id))
        record = self.env[self._expose_model].search(domain)
        if not record:
            raise MissingError(
                _('The record %s %s does not exist') % (
                    self._expose_model, _id))
        else:
            return record

    def _get_base_search_domain(self):
        return []
