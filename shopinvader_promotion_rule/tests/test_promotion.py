# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.tests.common import CommonCase
from openerp.addons.shopinvader.services.cart import CartService
from openerp.addons.sale_promotion_rule.tests.test_promotion import (
    AbstractPromotionCase)
from openerp.addons.sale_delivery_promotion_rule.tests.test_promotion import (
    AbstractPromotionDeliveryCase)


class ShopinvaderPromotionCase(CommonCase, AbstractPromotionCase):

    def add_coupon_code(self, coupon_code):
        self.service.update({'coupon_code': coupon_code})

    def setUp(self, *args, **kwargs):
        super(ShopinvaderPromotionCase, self).setUp(*args, **kwargs)
        self.set_up('shopinvader.sale_order_3')
        self.promotion_rule.apply_discount_on = 'all'
        self.shopinvader_session = {'cart_id': self.sale.id}
        self.partner = self.env.ref('shopinvader.partner_2')
        self.service = self._get_service(CartService, self.partner)


class ShopinvaderPromotionDeliveryCase(CommonCase,
                                       AbstractPromotionDeliveryCase):

    def add_coupon_code(self, coupon_code):
        self.service.update({'coupon_code': coupon_code})

    def setUp(self, *args, **kwargs):
        super(ShopinvaderPromotionDeliveryCase, self).setUp(*args, **kwargs)
        self.set_up('shopinvader.sale_order_3')
        self.shopinvader_session = {'cart_id': self.sale.id}
        self.partner = self.env.ref('shopinvader.partner_2')
        self.service = self._get_service(CartService, self.partner)
