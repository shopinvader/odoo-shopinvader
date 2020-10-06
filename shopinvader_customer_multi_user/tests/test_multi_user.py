# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon

_logger = logging.getLogger(__name__)


class TestCustomer(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_binding = cls._create_partner(
            cls.env, invader_user_token="ABCDEF"
        )
        cls.company = cls.company_binding.record_id

    @staticmethod
    def _create_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader.backend_1").id,
            "is_company": True,
            "name": "ACME ltd",
            "external_id": "acme",
            "email": "company@test.com",
            "ref": "#ACME",
        }
        values.update(kw)
        return env["shopinvader.partner"].create(values)

    def test_token_manual_override(self):
        self.assertEqual(self.company.invader_user_token, "ABCDEF")

    def _generate_random_companies(self, count=5):
        tokens = set()
        for x in range(5):
            comp = self._create_partner(self.env, email="acme%s@test.com" % x)
            if comp.invader_user_token:
                tokens.add(comp.invader_user_token)
        return tokens

    def test_token_auto_gen_disabled(self):
        self.assertFalse(self.backend.customer_multi_user)
        tokens = self._generate_random_companies()
        self.assertEqual(len(tokens), 0)

    def test_token_auto_gen(self):
        self.backend.customer_multi_user = True
        tokens = self._generate_random_companies()
        self.assertEqual(len(tokens), 5)

    def test_create_customer_no_multi_user(self):
        self.data.update({"external_id": "cust1"})
        params = dict(self.data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertFalse(partner.parent_id)
        self.assertFalse(partner.is_invader_user)
        self._test_partner_data(partner, self.data)

    def test_create_customer_multi_user(self):
        self.backend.customer_multi_user = True
        data = dict(
            self.data, external_id="new1", email="new@one.com", name="New One"
        )
        # customer 1
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner1 = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner1.parent_id, self.company)
        self.assertEqual(partner1.type, "contact")
        self.assertTrue(partner1.is_invader_user)
        self._test_partner_data(partner1, data)
        # customer 2
        data = dict(
            self.data, external_id="new2", email="new@two.com", name="New Two"
        )
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner2 = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner2.parent_id, self.company)
        self.assertEqual(partner2.type, "contact")
        self.assertTrue(partner2.is_invader_user)
        self._test_partner_data(partner2, data)
        # both are there
        self.assertIn(partner1, self.company.child_ids)
        self.assertIn(partner2, self.company.child_ids)
        # the company is not an invader user
        self.assertFalse(self.company.is_invader_user)

    def test_create_customer_multi_user_wrong_token(self):
        self.data.update({"external_id": "cust1"})
        params = dict(self.data, company_token="WRONG_TOKEN")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # partner is created normally, no relation w/ the company
        self.assertFalse(partner.parent_id)
        self.assertFalse(partner.is_invader_user)
        self._test_partner_data(partner, self.data)
        self.assertNotIn(partner, self.company.child_ids)
        self.assertFalse(self.company.is_invader_user)

    def test_get_customer_partner(self):
        self.backend.customer_multi_user = True
        data = dict(
            self.data, external_id="cust1", email="new@one.com", name="New One"
        )
        # customer 1
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner1 = self.env["res.partner"].browse(res["id"])
        binding1 = partner1._get_invader_partner(self.backend)
        # partner is the parent company
        self.assertTrue(binding1.is_invader_user)
        self.assertEqual(
            partner1.get_customer_partner(self.backend), self.company
        )
        self.assertEqual(
            self.company.get_customer_partner(self.backend), self.company
        )

    def test_customer_data(self):
        res = self.service._to_customer_info(self.company)
        self.assertEqual(res["company_token"], "ABCDEF")
        self.assertEqual(
            res["main_account"],
            {
                "id": self.company.id,
                "name": self.company.name,
                "ref": self.company.ref,
            },
        )
