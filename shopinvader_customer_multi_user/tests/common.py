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
        # Create 2 more users so that we have
        # 1 company user with 3 simple users
        # and user 3 is a child of user 2.
        cls.user_binding2 = cls._create_partner(
            cls.env,
            name="Simple user 2",
            parent_id=cls.company.id,
            external_id="simple-user-2",
            email="simpleuser2@test.com",
        )
        cls.user_binding3 = cls._create_partner(
            cls.env,
            name="Simple user 3",
            parent_id=cls.user_binding2.record_id.id,
            main_partner_id=cls.user_binding2.record_id.id,
            external_id="simple-user-3",
            email="simpleuser3@test.com",
        )
        cls.backend.multi_user_records_policy = "record_id"
        cls.backend.customer_multi_user = True

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

    def _get_service(self, partner, usage="users"):
        with self.work_on_services(
            partner=partner, shopinvader_session=self.shopinvader_session
        ) as work:
            return work.component(usage=usage)


class TestUserManagementCommmon(TestMultiUserCommon):
    """Test interaction with /users endpoint."""

    def _get_service(self, partner, usage="users"):
        with self.work_on_services(partner=partner) as work:
            return work.component(usage=usage)

    def _test_search(self, service, expected):
        _res = sorted(service.dispatch("search")["data"], key=lambda x: x["email"])
        self.assertEqual(
            _res,
            [
                {
                    "email": x.email,
                    "id": x.id,
                    "name": x.name,
                    "parent_id": x.parent_id.id,
                    "can_manage_users": x.can_manage_users,
                }
                for x in expected.sorted("email")
            ],
        )

    def _test_create(self, service, params, expected_parent=None):
        partner = expected_parent or service.partner_user
        count_before = len(partner.child_ids)
        res = service.dispatch("create", params=params)["data"]
        self.assertEqual(len(partner.child_ids), count_before + 1)
        new_partner = partner.child_ids.filtered_domain(
            [("email", "=", params["email"])]
        )
        invader_partner = new_partner._get_invader_partner(self.backend)
        expected = dict(
            params,
            parent_id=partner.id,
            id=invader_partner.id,
            can_manage_users=invader_partner.can_manage_users,
        )
        self.assertEqual(res, expected)
        return invader_partner
