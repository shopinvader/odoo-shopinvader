# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import ShoptorService
from .contact import ContactService


class AbstractSaleService(ShoptorService):

    def _parser_product(self):
        fields = ['name', 'id']
        if 'product_code_builder' in self.env.registry._init_modules:
            fields.append('prefix_code')
        return fields

    def _parser_order_line(self):
        parser = [
            'id',
            ('product_id', self._parser_product()),
            'product_url',
            'price_unit',
            'product_uom_qty',
            'price_subtotal',
            'discount',
            'is_delivery',
            ]
        if 'sale_order_line_price_subtotal_gross' in\
                self.env.registry._init_modules:
            parser.append('price_subtotal_gross')
        return parser

    def _parser_partner(self):
        return ['id', 'display_name', 'ref']

    def _parser_carrier(self):
        return ['id', 'name', 'description']

    def _parser(self):
        contact_parser = self.service_for(ContactService)._json_parser()
        return [
            'id',
            'name',
            'amount_total',
            'amount_untaxed',
            'amount_tax',
            'shipping_amount_total',
            'shipping_amount_untaxed',
            'shipping_amount_tax',
            'item_amount_total',
            'item_amount_untaxed',
            'item_amount_tax',
            'cart_state',
            'anonymous_email',
            'state',
            ('carrier_id', self._parser_carrier()),
            ('partner_id', self._parser_partner()),
            ('partner_shipping_id', contact_parser),
            ('partner_invoice_id', contact_parser),
            ('order_line', self._parser_order_line()),
        ]

    def _to_json(self, sale):
        return sale.jsonify(self._parser())
