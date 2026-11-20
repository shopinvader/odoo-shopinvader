# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from functools import partial

from fastapi import status
from requests import Response

from odoo.tests.common import tagged
from odoo.tools import mute_logger

from odoo.addons.auth_partner.tests.common import CommonTestAuthPartner
from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi.dependencies import fastapi_endpoint
from odoo.addons.shopinvader_unit_management.tests.common import (
    TestUnitManagementCommon,
)

from ..routers import unit_member_router


@tagged("post_install", "-at_install")
class TestShopinvaderFastapiAuthPartnerApiUnitMember(
    FastAPITransactionCase, TestUnitManagementCommon, CommonTestAuthPartner
):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.directory.member_existing_template_id = cls.env.ref(
            "shopinvader_fastapi_auth_partner_api_unit_member.email_already_existing",
        )
        # Set emails
        managers = [1, 2, 0, 2]
        collaborators = [5, 3, 3, 0]
        for unit in range(1, 5):
            for manager in range(1, 1 + managers[unit - 1]):
                mail = f"manager_{unit}_{manager}@example.org"
                manager = getattr(
                    cls,
                    f"manager_{unit}_{manager}",
                )
                manager.email = mail
            for collaborator in range(1, 1 + collaborators[unit - 1]):
                mail = f"collaborator_{unit}_{collaborator}@example.org"
                collaborator = getattr(
                    cls,
                    f"collaborator_{unit}_{collaborator}",
                )
                collaborator.email = mail

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_unit_member."
                                "shopinvader_unit_management_user_group"
                            ).id
                        ],
                    )
                ],
            }
        )

        cls.default_fastapi_authenticated_partner = cls.manager_1_1
        cls.default_fastapi_router = unit_member_router
        cls.demo_app = cls.env.ref("fastapi_auth_partner.fastapi_endpoint_demo")
        cls.default_fastapi_app = cls.demo_app._get_app()
        cls.default_fastapi_dependency_overrides = {
            fastapi_endpoint: partial(lambda a: a, cls.demo_app)
        }

    @contextmanager
    def _create_test_client(self, **kwargs):
        kwargs.setdefault("raise_server_exceptions", False)
        with mute_logger("httpx"), super()._create_test_client(**kwargs) as test_client:
            yield test_client

    def test_unit_auth_state(self):
        self.default_fastapi_authenticated_partner = self.manager_1_1

        with self._create_test_client() as test_client:
            response: Response = test_client.get("/unit/members")
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        members = response.json()
        self.assertEqual(len(members), 6)
        for member in members:
            self.assertEqual(member["auth_state"], "none")

    def test_invite_unit_member_as_collaborator(self):
        self.default_fastapi_authenticated_partner = self.collaborator_1_1

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_2.id}/invite"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_invite_unit_member_as_manager(self):
        self.default_fastapi_authenticated_partner = self.manager_1_1
        self.assertFalse(self.collaborator_1_2.auth_partner_ids)
        auth_partner_len = self.env["auth.partner"].search_count([])
        with self._create_test_client() as test_client, self.new_mails() as new_mails:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_2.id}/invite"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )
        self.assertTrue(self.collaborator_1_2.auth_partner_ids)
        self.assertEqual(
            self.env["auth.partner"].search_count([]), auth_partner_len + 1
        )
        self.assertEqual(len(new_mails), 1)
        self.assertEqual(
            new_mails.subject,
            "Welcome",
        )
        self.assertIn(
            "your account have been created",
            new_mails.body,
        )

    def test_invite_existing_unit_member_as_manager(self):
        self.default_fastapi_authenticated_partner = self.manager_1_1
        self.collaborator_1_2.auth_partner_ids = [
            (
                0,
                0,
                {
                    "login": self.collaborator_1_2.email,
                    "directory_id": self.directory.id,
                },
            )
        ]

        self.assertTrue(self.collaborator_1_2.auth_partner_ids)
        auth_partner_len = self.env["auth.partner"].search_count([])
        with self._create_test_client() as test_client, self.new_mails() as new_mails:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_2.id}/invite"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )
        self.assertTrue(self.collaborator_1_2.auth_partner_ids)
        self.assertEqual(self.env["auth.partner"].search_count([]), auth_partner_len)
        self.assertEqual(len(new_mails), 1)
        self.assertEqual(new_mails.partner_ids, self.collaborator_1_2)
        self.assertEqual(
            new_mails.subject,
            "Welcome",
        )
        self.assertIn(
            "your account have been created",
            new_mails.body,
        )

    def test_invite_existing_other_unit_member_as_manager(self):
        self.default_fastapi_authenticated_partner = self.manager_1_1
        self.collaborator_2_1.email = self.collaborator_1_2.email
        self.collaborator_2_1.auth_partner_ids = [
            (
                0,
                0,
                {
                    "login": self.collaborator_2_1.email,
                    "directory_id": self.directory.id,
                },
            )
        ]

        self.assertFalse(self.collaborator_1_2.auth_partner_ids)
        auth_partner_len = self.env["auth.partner"].search_count([])
        with self._create_test_client() as test_client, self.new_mails() as new_mails:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_2.id}/invite"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
        self.assertFalse(self.collaborator_1_2.auth_partner_ids)
        self.assertEqual(self.env["auth.partner"].search_count([]), auth_partner_len)
        self.assertEqual(len(new_mails), 1)
        self.assertEqual(new_mails.partner_ids, self.collaborator_2_1)
        self.assertEqual(
            new_mails.subject,
            "Someone tried to invite you in an other team",
        )
        self.assertIn(
            "Hi Collaborator 2.1",
            new_mails.body,
        )
        self.assertIn(
            "Manager 1.1 tried to invite you in the team",
            new_mails.body,
        )
        self.assertIn(
            "Unit 1 but you already have an",
            new_mails.body,
        )
        self.assertIn(
            "other account, please contact Manager 1.1",
            new_mails.body,
        )

    def test_invite_unit_auth_state(self):
        self.default_fastapi_authenticated_partner = self.manager_1_1

        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                f"/unit/members/{self.collaborator_1_2.id}",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        member = response.json()
        self.assertEqual(member["auth_state"], "none")

        with self._create_test_client() as test_client, self.new_mails():
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_2.id}/invite"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        member = response.json()
        self.assertEqual(member["auth_state"], "invited")

        self.collaborator_1_2.auth_partner_ids.write({"password": "test"})

        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                f"/unit/members/{self.collaborator_1_2.id}",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        member = response.json()
        self.assertEqual(member["auth_state"], "accepted")
