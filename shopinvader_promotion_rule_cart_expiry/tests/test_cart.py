# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.addons.sale_promotion_rule.tests.test_promotion import (
    AbstractCommonPromotionCase,
)
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase, AbstractCommonPromotionCase):
    def setUp(self, *args, **kwargs):
        super(TestCart, self).setUp(*args, **kwargs)
        self.set_up("shopinvader.sale_order_2")
        self.product_1 = self.env.ref("product.product_product_4b")
        self.promo_rule_obj = self.env["sale.promotion.rule"]

    def test_shopinvader_write_date_on_compute_promotions(self):
        """
        Ensure the shopinvader_write_date is not updated during compute_promotions
        :return:
        """
        # Test when the field is empty
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": False}
        )
        self.assertFalse(self.sale.shopinvader_write_date)
        self.promo_rule_obj.compute_promotions(self.sale)
        self.sale.refresh()
        self.assertFalse(self.sale.shopinvader_write_date)
        # Re-check with the field is set with a value
        custom_date = "2020-01-01 00:00:00"
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": custom_date}
        )
        self.assertEquals(self.sale.shopinvader_write_date, custom_date)
        self.promo_rule_obj.compute_promotions(self.sale)
        self.sale.refresh()
        self.assertEquals(self.sale.shopinvader_write_date, custom_date)

    def test_shopinvader_write_date_classic_write(self):
        """
        Ensure the shopinvader_write_date is correctly updated in case of normal write
        :return:
        """
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": False}
        )
        self.assertFalse(self.sale.shopinvader_write_date)
        self.sale.write({"note": "A text"})
        self.assertTrue(self.sale.shopinvader_write_date)
        # Now ensure it's correctly updated at each write. So do a second write
        custom_date = "2020-01-01 00:00:00"
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": custom_date}
        )
        self.sale.write({"note": "A new text"})
        self.assertTrue(self.sale.shopinvader_write_date)
        self.assertNotEquals(self.sale.shopinvader_write_date, custom_date)

    def test_cart_expiry_delete(self):
        """
        Ensure the domain (_get_expiry_cart_domain on shopinvader backend) is correct
        and the cart/SO is included into it.
        :return:
        """
        # The cart shouldn't be deleted because it considered as a new one.
        now = fields.Datetime.now()
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": now}
        )
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "delete"}
        )
        self.backend.manage_cart_expiry()
        self.assertTrue(self.sale.exists())
        self.assertEqual(self.sale.state, "draft")
        # Now set the shopinvader_write_date with an old date and it should be removed.
        self.sale.with_context(skip_shopinvader_write_date=True).write(
            {"shopinvader_write_date": "2020-01-01 00:00:00"}
        )
        self.backend.manage_cart_expiry()
        self.assertFalse(self.sale.exists())
