# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from os import urandom

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestMultiUserCommon(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_binding = cls._create_partner(
            cls.env, invader_user_token="ABCDEF", is_company=True
        )
        cls.company = cls.company_binding.record_id
        cls.user_binding = cls._create_partner(
            cls.env,
            name="Simple user",
            parent_id=cls.company.id,
            external_id="simple-user",
            email="simpleuser@test.com",
        )
        cls.backend.multi_user_records_policy = "record_id"

    @staticmethod
    def _get_random_hash():
        """
        returns a positive integer from hashing 4 random bytes
        """
        return abs(hash(urandom(4)))

    @staticmethod
    def _create_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader.backend_1").id,
            "name": "ACME ltd",
            "external_id": "acme",
            "email": "company@test.com",
            "ref": "#ACME",
        }
        values.update(kw)
        values["external_id"] = values["external_id"] + str(
            TestMultiUserCommon._get_random_hash()
        )
        return env["shopinvader.partner"].create(values)
