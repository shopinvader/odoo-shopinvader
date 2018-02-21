# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.abstract.sale.service'

    def _parser_product(self):
        fields = ['name', 'object_id:id', 'url_key', 'images', 'default_code']
        if 'product_code_builder' in self.env.registry._init_modules:
            fields.append('prefix_code')
        return fields

    def _parser_order_line(self):
        parser = [
            'id',
            ('shopinvader_variant_id:product', self._parser_product()),
            'price_unit',
            'product_uom_qty',
            'price_subtotal',
            'discount',
            ]
        if 'sale_order_line_price_subtotal_gross' in\
                self.env.registry._init_modules:
            parser.append('price_subtotal_gross')
        return parser

    def _parser_partner(self):
        return ['id', 'display_name', 'ref']

    def _parser(self):
        address_parser = self.component(usage='address')._json_parser()
        return [
            'id',
            'name',
            'amount_total',
            'amount_untaxed',
            'amount_tax',
            'shopinvader_state:state',
            'date_order',
            ('partner_id:partner', self._parser_partner()),
            ('partner_shipping_id:partner_shipping', address_parser),
            ('partner_invoice_id:partner_invoice', address_parser),
            ('order_line', self._parser_order_line()),
        ]

    def _to_json(self, sale):
        res = sale.jsonify(self._parser())
        for order in res:
            order['item_number'] = sum([
                l['product_uom_qty']
                for l in order['order_line']])
            order['use_different_invoice_address'] = (
                order['partner_shipping']['id'] !=
                order['partner_invoice']['id'])
            for key in ['partner', 'partner_shipping', 'partner_invoice']:
                if order[key]['id'] ==\
                        self.locomotive_backend.anonymous_partner_id.id:
                    order[key] = {}
        return res
