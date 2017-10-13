# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.tests.common import CommonCase
from openerp.addons.shopinvader.services.cart import CartService
from openerp.exceptions import Warning as UserError


class DiscountCodeCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(DiscountCodeCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref('shopinvader.sale_order_3')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.partner_2')
        self.address = self.env.ref('shopinvader.partner_2_address_1')
        self.discount_code = self.env.ref('sale_discount_code.rule_1')
        self.service = self._get_service(CartService, self.partner)

    def test_add_good_discount_code(self):
        cart = self.service.update({'discount_code': 'ELDONGHUT'})
        for line in self.cart.order_line:
            self.assertEqual(line.discount_rule_id, self.discount_code)
            self.assertEqual(line.discount, self.discount_code.discount_amount)

    def test_add_bad_discount_code(self):
        with self.assertRaises(UserError):
            self.service.update({'discount_code': 'DGRVBYTHT'})

