# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.test_cart import CartCase


class TestCartPricelist(CartCase):
    def setUp(self, *args, **kwargs):
        super(TestCartPricelist, self).setUp(*args, **kwargs)
        self.partner = self.backend.anonymous_partner_id
        self.product_1 = self.env.ref("product.product_product_4b")
        self.sale_obj = self.env["sale.order"]

        self.pricelist_no_profile = self.env["product.pricelist"].create(
            {"name": "TEST no profile"}
        )
        self.backend.pricelist_id = False
        self.backend.use_sale_profile = True
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_cart_pricelist_profile(self):
        """
        If the partner pricelist is listed on sale profiles
        it should keep this one
        """
        self.assertEqual(
            self.partner.property_product_pricelist,
            self.env.ref("product.list0"),
        )
        cart = self.service._get()
        self.assertEqual(cart.pricelist_id, self.env.ref("product.list0"))

    def test_cart_pricelist_no_profile(self):
        """
        If the partner pricelist is not listed on sale profiles it should
        take the default one
        """
        self.partner.write({"property_product_pricelist": self.pricelist_no_profile.id})
        self.assertEqual(
            self.partner.property_product_pricelist.id,
            self.pricelist_no_profile.id,
        )
        cart = self.service._get()
        self.assertEqual(cart.pricelist_id, self.env.ref("product.list0"))
