# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector_locomotivecms.backend import locomotivecms
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.connector_generic.unit.mapper import GenericExportMapper


@locomotivecms
class ProductExportMapper(GenericExportMapper):
    _model_name = 'locomotivecms.product'

    direct = [
        ('name', 'name'),
        ('prefix_code', 'prefix_code'),
        ('url_key', 'url_key'),
        ('id', 'id'),
        ]

    def _apply(self, map_record, options=None):
        res = super(ProductExportMapper, self)._apply(map_record, options=options)
        res.update({
            'stock_state': 'En stock',
            'from_price': 10, # en tenant compte des qty
            'discount_old_price': 15,
            'thunbmail': 'http://...',
            'discount_value': 25,
            'cross_sell_ids': [],
            'related_ids': [],
            'up_selling_ids': [],
            })
        return {
            'is_discounted': True,
            'is_bestseller': True,
            'is_bestdiscount': True,
            'data': res,
            'name': res['prefix_code'],
            '_slug': res['url_key'],
            'odoo_id': str(res.pop('id')),
            }
