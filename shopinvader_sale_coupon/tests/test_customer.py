from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.shopinvader_restapi.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super(TestCustomer, cls).setUpClass()
        cls.ten_percent_program = cls.env["coupon.program"].create(
            {
                "name": "10%",
                "promo_code_usage": "code_needed",
                "reward_type": "discount",
                "discount_type": "percentage",
                "discount_percentage": 10,
                "validity_duration": 5,
                "active": True,
            }
        )
        cls.ten_dollar_program = cls.env["coupon.program"].create(
            {
                "name": "10$",
                "promo_code_usage": "code_needed",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 10,
                "active": True,
            }
        )

    def set_coupon_create_date(self, coupon, newdate):
        self.env.cr.execute(
            "UPDATE coupon_coupon SET create_date = %s WHERE id = %s",
            (fields.Datetime.to_string(newdate), coupon.id),
        )
        coupon._cache.clear()

    def test_get_customer_no_coupons(self):
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertNotIn("valid_coupons_ids", data)

    def test_get_customer_coupons(self):
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {
                "generation_type": "nbr_customer",
                "partners_domain": "[('id', 'in', [%s])]" % (self.partner.id),
            }
        ).generate_coupon()
        coupon = self.ten_percent_program.coupon_ids
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.ten_dollar_program.id
        ).create(
            {
                "generation_type": "nbr_customer",
                "partners_domain": "[('id', 'in', [%s])]" % (self.partner_2.id),
            }
        ).generate_coupon()
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 5,
            }
        ).generate_coupon()

        data = self.service_with_partner.dispatch("get")["data"]
        self.assertIn("valid_coupons_ids", data)
        self.assertEqual(data["valid_coupons_ids"]["count"], 1)
        self.assertEqual(len(data["valid_coupons_ids"]["items"]), 1)
        item = data["valid_coupons_ids"]["items"][0]
        self.assertEqual(item["code"], coupon.code)
        self.assertEqual(item["state"], "sent")
        self.assertEqual(item["program"]["id"], self.ten_percent_program.id)
        self.assertEqual(item["program"]["name"], "10%")

        coupon.state = "cancel"
        data = self.service_with_partner.dispatch("get")["data"]
        self.assertNotIn("valid_coupons_ids", data)

    def test_get_customer_coupons_expiration(self):
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.ten_percent_program.id
        ).create(
            {
                "generation_type": "nbr_customer",
                "partners_domain": "[('id', 'in', [%s])]" % (self.partner.id),
            }
        ).generate_coupon()

        percentage_coupon = self.ten_percent_program.coupon_ids
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.ten_dollar_program.id
        ).create(
            {
                "generation_type": "nbr_customer",
                "partners_domain": "[('id', 'in', [%s])]" % (self.partner.id),
            }
        ).generate_coupon()

        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 2)
        self.assertEqual(
            data["valid_coupons_ids"]["items"][0]["program"]["name"], "10%"
        )
        self.assertEqual(
            data["valid_coupons_ids"]["items"][1]["program"]["name"], "10$"
        )

        self.set_coupon_create_date(
            percentage_coupon, fields.Datetime.now() - relativedelta(days=5)
        )

        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 2)

        self.set_coupon_create_date(
            percentage_coupon, fields.Datetime.now() - relativedelta(days=6)
        )

        data = self.service_with_partner.dispatch("get")["data"]
        self.assertEqual(data["valid_coupons_ids"]["count"], 1)
