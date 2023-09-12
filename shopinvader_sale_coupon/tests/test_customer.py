from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.shopinvader_restapi.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super(TestCustomer, cls).setUpClass()
        cls.ten_percent_program = cls.env["loyalty.program"].create(
            {
                "name": "10% with code",
                "program_type": "coupons",
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 10,
                            "discount_mode": "percent",
                        },
                    )
                ],
            }
        )
        cls.ten_dollar_program = cls.env["loyalty.program"].create(
            {
                "name": "10$ with code",
                "program_type": "coupons",
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 10,
                            "discount_mode": "per_order",
                        },
                    )
                ],
            }
        )
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "list_price": 100,
                "sale_ok": True,
            }
        )
        cls.free_product_program = cls.env["loyalty.program"].create(
            {
                "name": "Free product A",
                "program_type": "coupons",
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "product",
                            "reward_product_id": cls.product_A.id,
                        },
                    )
                ],
            }
        )

    def test_get_customer_no_coupons(self):
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertNotIn("valid_coupons_ids", data)

    def test_get_customer_coupons(self):
        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {"mode": "selected", "customer_ids": [(4, self.partner.id)]}
        ).generate_coupons()
        coupon = self.ten_percent_program.coupon_ids
        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.ten_dollar_program.id
        ).create(
            {"mode": "selected", "customer_ids": [(4, self.partner_2.id)]}
        ).generate_coupons()

        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {
                "coupon_qty": 5,
            }
        ).generate_coupons()
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertIn("valid_coupons_ids", data)
        self.assertEqual(data["valid_coupons_ids"]["count"], 1)
        self.assertEqual(len(data["valid_coupons_ids"]["items"]), 1)
        item = data["valid_coupons_ids"]["items"][0]
        self.assertEqual(item["code"], coupon.code)
        self.assertEqual(item["program"]["id"], self.ten_percent_program.id)
        self.assertEqual(item["program"]["name"], "10% with code")

        coupon.expiration_date = fields.Date.today() - relativedelta(days=1)
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertNotIn("valid_coupons_ids", data)

    def test_get_customer_coupons_expiration(self):
        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {"mode": "selected", "customer_ids": [(4, self.partner.id)]}
        ).generate_coupons()

        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.ten_dollar_program.id
        ).create(
            {"mode": "selected", "customer_ids": [(4, self.partner.id)]}
        ).generate_coupons()
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 2)
        self.assertEqual(
            data["valid_coupons_ids"]["items"][0]["program"]["name"], "10% with code"
        )
        self.assertEqual(
            data["valid_coupons_ids"]["items"][1]["program"]["name"], "10$ with code"
        )

        # Update the validity on the program: 5 days.
        self.ten_percent_program.date_to = fields.Date.today() - relativedelta(days=1)
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 1)

    def test_get_customer_coupons_free_product(self):
        self.env["loyalty.generate.wizard"].with_context(
            active_id=self.free_product_program.id
        ).create(
            {"mode": "selected", "customer_ids": [(4, self.partner.id)]}
        ).generate_coupons()
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 1)
        self.assertEqual(
            data["valid_coupons_ids"]["items"][0]["program"]["id"],
            self.free_product_program.id,
        )
        self.assertEqual(
            len(data["valid_coupons_ids"]["items"][0]["program"]["rewards"]), 1
        )
        self.assertEqual(
            data["valid_coupons_ids"]["items"][0]["program"]["rewards"][0][
                "reward_product"
            ]["id"],
            self.product_A.id,
        )
