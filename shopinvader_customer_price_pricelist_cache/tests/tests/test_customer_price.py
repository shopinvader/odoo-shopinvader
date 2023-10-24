# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class CommonCustomerPriceCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env.ref("shopinvader.partner_1")
        cls.partner2 = cls.env.ref("shopinvader.partner_2")
        cls.discount_pricelist = cls.env.ref("shopinvader.pricelist_1")
        cls.fiscal_pos1 = cls.env.ref("shopinvader.fiscal_position_0")
        cls.fiscal_pos2 = cls.env.ref("shopinvader.fiscal_position_2")
        cls.pricelist_field = cls.env.ref(
            "product.field_res_partner__property_product_pricelist"
        )
        cls.backend.cart_pricelist_partner_field_id = cls.pricelist_field
        # Base case, no cache
        cls.env["product.pricelist.cache"].flush_pricelist_cache()

    def _get_service(self, partner):
        with self.work_on_services(partner=partner) as work:
            return work.component(usage="customer_price")

    def _test_response(self, res, s_variant, expected_price):
        expected = {
            "id": s_variant.record_id.id,
            "price": {"default": expected_price},
        }
        self.assertEqual(res, expected)

    def create_cache(self):
        self.env["product.pricelist.cache"].cron_reset_pricelist_cache()

    def test_get_price_default_with_cache(self):
        self.create_cache()
        s_variant = self.shopinvader_variant
        service = self._get_service(self.partner1)
        # partner1
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        self._test_response(res, s_variant, expected_price)
        # partner2
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos2
        )
        service = self._get_service(self.partner2)
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        self._test_response(res, s_variant, expected_price)

    def test_get_price_default_without_cache(self):
        s_variant = self.shopinvader_variant
        service = self._get_service(self.partner1)
        # partner1
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        self._test_response(res, s_variant, expected_price)
        # partner2
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos2
        )
        service = self._get_service(self.partner2)
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        self._test_response(res, s_variant, expected_price)

    def test_get_price_custom_pricelist_with_cache(self):
        self.create_cache()
        s_variant = self.shopinvader_variant
        self.partner1.property_product_pricelist = self.discount_pricelist
        # partner1
        service = self._get_service(self.partner1)
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        expected_price = s_variant._get_price(
            pricelist=self.discount_pricelist, fposition=self.fiscal_pos1
        )
        self._test_response(res, s_variant, expected_price)

    def test_get_price_custom_pricelist_without_cache(self):
        s_variant = self.shopinvader_variant
        self.partner1.property_product_pricelist = self.discount_pricelist
        # partner1
        service = self._get_service(self.partner1)
        res = service.dispatch(
            "products", params={"ids": s_variant.record_id.ids, "one": True}
        )
        expected_price = s_variant._get_price(
            pricelist=self.discount_pricelist, fposition=self.fiscal_pos1
        )
        self._test_response(res, s_variant, expected_price)

    def test_get_price_multi_with_cache(self):
        self.create_cache()
        s_variant = self.shopinvader_variant
        prod2 = self.env.ref("product.product_product_11")
        s_variant2 = prod2.shopinvader_bind_ids[0]
        service = self._get_service(self.partner1)
        res = service.dispatch(
            "products",
            params={"ids": [s_variant.record_id.id, s_variant2.record_id.id]},
        )
        self.assertEqual(len(res), 2)
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res1 = [x for x in res if x["id"] == s_variant.record_id.id][0]
        self._test_response(res1, s_variant, expected_price)
        expected_price = s_variant2._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res2 = [x for x in res if x["id"] == s_variant2.record_id.id][0]
        self._test_response(res2, s_variant2, expected_price)

    def test_get_price_multi_without_cache(self):
        s_variant = self.shopinvader_variant
        prod2 = self.env.ref("product.product_product_11")
        s_variant2 = prod2.shopinvader_bind_ids[0]
        service = self._get_service(self.partner1)
        res = service.dispatch(
            "products",
            params={"ids": [s_variant.record_id.id, s_variant2.record_id.id]},
        )
        self.assertEqual(len(res), 2)
        expected_price = s_variant._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res1 = [x for x in res if x["id"] == s_variant.record_id.id][0]
        self._test_response(res1, s_variant, expected_price)
        expected_price = s_variant2._get_price(
            pricelist=self.base_pricelist, fposition=self.fiscal_pos1
        )
        res2 = [x for x in res if x["id"] == s_variant2.record_id.id][0]
        self._test_response(res2, s_variant2, expected_price)
