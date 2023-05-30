# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.tests.test_cart_item import ItemCaseMixin


class ConnectedItemCase(ItemCaseMixin, CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_products()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.custom_pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist"}
        )
        cls.partner.property_product_pricelist = cls.custom_pricelist
        cls.pricelist_field = cls.env.ref(
            "product.field_res_partner__property_product_pricelist"
        )

    def setUp(self):
        super().setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="cart")

    def test_default_pricelist(self):
        self.assertFalse(self.backend.cart_pricelist_partner_field_id)
        cart = self.service._get()
        self.assertEqual(cart.pricelist_id, self.partner.property_product_pricelist)

    def test_custom_pricelist(self):
        self.backend.cart_pricelist_partner_field_id = self.pricelist_field
        cart = self.service._get()
        self.assertEqual(cart.pricelist_id, self.custom_pricelist)
