# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase
from ..http import convert_nested_html_form_params


class CommonCase(TransactionCase):

    def test_nested_form(self):
        result = convert_nested_html_form_params({
            'sale_order_line[0][qty]': u'1',
            'sale_order_line[0][id]': u'325761',
            'sale_order_line[1][qty]': u'3',
            'sale_order_line[1][id]': u'325762',
            'message': u'my message',
            'subject_id': u'2'})
        self.assertEqual(result, {
            'message': u'my message',
            'subject_id': u'2',
            'sale_order_line': [
                {'id': u'325761', 'qty': u'1'},
                {'id': u'325762', 'qty': u'3'}
                ]
            })
