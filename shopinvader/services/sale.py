# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .helper import to_int, secure_params
from .abstract_sale import AbstractSaleService
from openerp.addons.connector_locomotivecms.backend import locomotive
from werkzeug.exceptions import NotFound


@locomotive
class SaleService(AbstractSaleService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def list(self, params):
        domain = [('partner_id', '=', self.partner.id)]
        domain += params.get('domain', [])
        sale_obj = self.env['sale.order']
        total_count = sale_obj.search_count(domain)
        page = params.get('page', 1)
        per_page = params.get('per_page', 5)
        orders = sale_obj.search(
            domain, limit=per_page, offset=per_page*(page-1))
        return {
            'size': total_count,
            'data': self._to_json(orders),
            }

    @secure_params
    def get(self, params):
        order = self._get(params['id'])
        return self._to_json(order)[0]

    # Validator
    def _validator_get(self):
        return {
            'id': {'coerce': to_int, 'required': True}
            }

    def _validator_list(self):
        return {
            'per_page': {
                'coerce': to_int,
                'nullable': True,
                },
            'page': {
                'coerce': to_int,
                'nullable': True,
                },
            'domain': {
                'coerce': self.to_domain,
                'nullable': True,
                },
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get(self, order_id):
        order = self.env['sale.order'].search([
            ('id', '=', order_id),
            ('partner_id', '=', self.partner.id),
            ('locomotive_backend_id', '=', self.backend_record.id),
            ])
        if not order:
            raise NotFound('The order %s does not exist' % order_id)
        else:
            return order
