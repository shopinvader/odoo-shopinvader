# Copyright 2022 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.shopinvader.tests.test_cart_item import ItemCaseMixin


class SaleProfileCartTest(ItemCaseMixin, ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        vals = {
            "name": "Pricelist Shopinvader Profile",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.variant.id,
                        "applied_on": "0_product_variant",
                        "base": "list_price",
                        "compute_price": "fixed",
                        "fixed_price": 400.0,
                        "base_pricelist_id": cls.base_pricelist.id,
                    },
                )
            ],
        }
        cls.pricelist_profile = cls.env["product.pricelist"].create(vals)

        vals = {
            "code": "SSP",
            "backend_id": cls.backend.id,
            "pricelist_id": cls.pricelist_profile.id,
        }
        cls.shopinvader_sale_profile = cls.env["shopinvader.sale.profile"].create(vals)

        cls.backend.use_sale_profile = True

    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_without_sale_profile_cart(self):
        """
        Check the item addition in cart without sale profile behaviour
        """
        cart_id = self.add_item(self.variant.id, 1)["id"]
        cart = self.env["sale.order"].browse(cart_id)
        line = cart.order_line
        self.assertEqual(
            line.price_unit,
            750.0,
        )

    def test_with_sale_profile_cart(self):
        """
        Check the item addition in cart with sale profile behaviour
        """
        self.partner.property_product_pricelist = self.pricelist_profile
        cart_id = self.add_item(self.variant.id, 1)["id"]
        cart = self.env["sale.order"].browse(cart_id)
        line = cart.order_line
        self.assertEqual(
            line.price_unit,
            400.0,
        )
