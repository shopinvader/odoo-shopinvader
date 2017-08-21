# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import ShopinvaderService
from .address import AddressService


class AbstractSaleService(ShopinvaderService):

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

    def _parser_payment_method(self):
        return [
            'id',
            'name',
            'description',
            'show_description_after_validation',
        ]

    def _parser(self):
        address_parser = self.service_for(AddressService)._json_parser()
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
            'anonymous_email',
            'anonymous_token',
            'shopinvader_state:state',
            'date_order',
            ('carrier_id:carrier', self._parser_carrier()),
            ('partner_id:partner', self._parser_partner()),
            ('partner_shipping_id:partner_shipping', address_parser),
            ('partner_invoice_id:partner_invoice', address_parser),
            ('order_line', self._parser_order_line()),
            ('payment_method_id:payment_method',
                self._parser_payment_method()),
        ]

    def _to_json(self, sale):
        res = sale.jsonify(self._parser())
        for order in res:
            order['order_line'] = [
                l for l in order['order_line']
                if not l['is_delivery']]
            order['item_number'] = sum([
                l['product_uom_qty']
                for l in order['order_line']])
            order['use_different_invoice_address'] = (
                order['partner_shipping']['id'] !=
                order['partner_invoice']['id'])
            for key in ['partner', 'partner_shipping', 'partner_invoice']:
                if order[key]['id'] ==\
                        self.backend_record.anonymous_partner_id.id:
                    order[key] = {}
            trackings = []
            sale_order = self.env['sale.order'].browse(order['id'])
            for picking in sale_order.picking_ids:
                for pack in picking._get_packages_from_picking():
                    if pack.parcel_tracking:
                        data = pack.with_context(
                            picking=self).open_tracking_url()
                        trackings.append({
                            'name': picking.carrier_id.name,
                            'url': data.get('url'),
                            'code': pack.parcel_tracking,
                            })
            order['trackings'] = trackings
        return res
