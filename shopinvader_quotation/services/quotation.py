# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class QuotationService(Component):
    _inherit = 'shopinvader.abstract.sale.service'
    _name = 'shopinvader.quotation.service'
    _usage = 'quotation'
    _expose_model = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        order = self._get(_id)
        return self._to_json(order)[0]

    def search(self, **params):
        return self._paginate_search(**params)

    # Validator
    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            'id': {'coerce': to_int},
            'per_page': {
                'coerce': to_int,
                'nullable': True,
                },
            'page': {
                'coerce': to_int,
                'nullable': True,
                },
            'scope': {
                'type': 'dict',
                'nullable': True,
                },
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get_base_search_domain(self):
        return [
            ('partner_id', '=', self.partner.id),
            ('shopinvader_backend_id', '=', self.shopinvader_backend.id),
            ('typology', '=', 'quotation'),
            ]
