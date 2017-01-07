# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _json_parser_cart_order(self):
        return [
            'name',
            'amount_total',
            'amount_untaxed',
            ('partner_id', ['id', 'display_name', 'ref']),
            ('order_line', [
                'id',
                ('product_id', ['name', 'id']),
                'price_unit',
                'product_uom_qty',
                'price_subtotal',
                ]),
        ]

    def _json_parser_history_order(self):
        # photo => url
        return [
            'state',
            'name',
            'date_order',
            ('carrier_id', ['name']),
            'amount_total',
            'amount_tax',
            'amount_untaxed',
            ('partner_shipping_id', [
                'id', 'display_name', 'ref', 'street',
                'street2', 'zip', 'city', 'phone',
                ('state_id', ['name']),
                ('country_id', ['name'])
                ]),
            ('partner_invoice_id', [
                'id', 'display_name', 'ref', 'street',
                'street2', 'zip', 'city', 'phone',
                ('state_id', ['name']),
                ('country_id', ['name'])
                ]),
            ('invoice_ids', ['id', 'number']),
            ('order_line', [
                'id',
                ('product_id', ['name', 'id']),
                'price_unit',
                'product_uom_qty',
                'price_subtotal',
                ]),
        ]

    @api.multi
    def to_json_cart(self):
        return self.jsonify(self._json_parser_cart_order())

    @api.multi
    def to_json_history(self):
        result = self.jsonify(self._json_parser_history_order())
        status_list = {
            'draft': 'quotation',
            'confirm': 'pending',
            # 'confirm': 'processing',
            'done': 'done',
            'cancel': 'cancel',
            }

        for order in result:
            order.update({
                'shipping_amount_tax_excluded': 10,
                'shipping_amount_tax_included': 12,
                'shipping_tax_amount': 2,
                'tracking': [{
                    'url': 'https://montracking',  # TODO
                    'value': '69DJSEO494394',
                    }],
                'payment_method_id': {'name': 'stripe'},
                'status': status_list.get(order['state'], 'processing'),
            })
            order.pop('state')
            for line in order['order_line']:
                line['product_image_url'] = 'http://todo.jpg'  # TODO
        return result

    @api.model
    def get_order_history(self, partner_id, per_page, page):
        domain = [('partner_id', '=', partner_id)]
        total_count = self.search_count(domain)
        orders = self.search(domain, limit=per_page, offset=per_page*(page-1))
        return {
            'total_count': total_count,
            'nbr_page': total_count/per_page + 1,
            'orders': orders.to_json_history(),
            }
