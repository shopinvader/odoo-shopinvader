# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from contextlib import contextmanager
from unittest import mock

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_unit_management.tests.common import (
    TestUnitManagementCommon,
)

from ..routers import unit_member_router


@tagged("post_install", "-at_install")
class TestShopinvaderApiUnitMember(FastAPITransactionCase, TestUnitManagementCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

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
        cls.default_fastapi_app = cls.env.ref(
            "fastapi.fastapi_endpoint_demo"
        )._get_app()

    @contextmanager
    def _rollback_called_test_client(self):
        with self._create_test_client() as test_client, mock.patch.object(
            self.env.cr.__class__, "rollback"
        ) as mock_rollback:
            yield test_client
            mock_rollback.assert_called_once()

    def test_get_manager_unit_members(self):
        """
        Test to get the manager unit members
        """
        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                "/unit/members",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        members = response.json()

        self.assertEqual(
            {member["id"] for member in members},
            set(
                (
                    self.manager_1_1
                    | self.collaborator_1_1
                    | self.collaborator_1_2
                    | self.collaborator_1_3
                    | self.collaborator_1_4
                    | self.collaborator_1_5
                ).ids
            ),
        )

    def test_collaborator_unit_members(self):
        """
        Test that a collaborator can't get the members of the unit
        """
        self.default_fastapi_authenticated_partner = self.collaborator_1_1

        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.get("/unit/members")
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_unit_unit_members(self):
        """
        Test that a unit can't get the members of the unit
        """
        self.default_fastapi_authenticated_partner = self.unit_1

        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.get("/unit/members")
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_get_manager_unit_member(self):
        """
        Test to get a manager unit member
        """
        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                f"/unit/members/{self.collaborator_1_1.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        member = response.json()
        self.assertEqual(member["id"], self.collaborator_1_1.id)
        self.assertEqual(member["name"], self.collaborator_1_1.name)
        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                f"/unit/members/{self.collaborator_1_2.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        member = response.json()
        self.assertEqual(member["id"], self.collaborator_1_2.id)
        self.assertEqual(member["name"], self.collaborator_1_2.name)

    def test_get_manager_unit_members_wrong_unit(self):
        """
        Test that a manager can't access members of another unit
        """
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.get(
                f"/unit/members/{self.collaborator_2_2.id}"
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
            )

    def test_get_manager_unit_members_wrong_type(self):
        """
        Test that a manager can't access a unit
        """
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.get(f"/unit/members/{self.unit_1.id}")
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
            )
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.get(f"/unit/members/{self.unit_2.id}")
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
            )

    def test_create_unit_member(self):
        """
        Test to create a new unit member
        """
        self.assertEqual(
            self.unit_1.member_ids,
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                "/unit/members",
                data=json.dumps(
                    {
                        "name": "New Unit Member",
                    }
                ),
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        member = response.json()
        new_member = self.env["res.partner"].browse(member["id"])
        self.assertEqual(member["name"], "New Unit Member")
        self.assertEqual(new_member.unit_id, self.unit_1)
        self.assertEqual(new_member.unit_profile, "collaborator")
        self.assertEqual(
            self.unit_1.member_ids,
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5
            | new_member,
        )

    def test_create_unit_manager(self):
        self.assertEqual(
            self.unit_1.member_ids,
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5,
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                "/unit/members",
                data=json.dumps({"name": "New Unit Manager", "type": "manager"}),
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        member = response.json()
        new_member = self.env["res.partner"].browse(member["id"])
        self.assertEqual(member["name"], "New Unit Manager")
        self.assertEqual(new_member.unit_id, self.unit_1)
        self.assertEqual(new_member.unit_profile, "manager")
        self.assertEqual(
            self.unit_1.member_ids,
            self.manager_1_1
            | self.collaborator_1_1
            | self.collaborator_1_2
            | self.collaborator_1_3
            | self.collaborator_1_4
            | self.collaborator_1_5
            | new_member,
        )

    def test_create_unit_wrong_type(self):
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post(
                "/unit/members",
                data=json.dumps({"name": "New Unit", "type": "unit"}),
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post(
                "/unit/members",
                data=json.dumps({"name": "New Unit", "type": "unknown"}),
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )

    def test_create_unit_wrong_partner(self):
        self.default_fastapi_authenticated_partner = self.collaborator_1_1
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post(
                "/unit/members",
                data=json.dumps({"name": "New Unit", "type": "collaborator"}),
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_update_unit_member(self):
        """
        Test to update a specific unit member
        """
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_4.id}",
                data=json.dumps(
                    {
                        "name": "Updated Unit Member",
                    }
                ),
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        member = response.json()
        updated_member = self.env["res.partner"].browse(member["id"])
        self.assertEqual(member["name"], "Updated Unit Member")
        self.assertEqual(updated_member.name, "Updated Unit Member")

        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Updated Unit Member",
                "Collaborator 1.5",
            },
        )

    def test_update_unit_manager(self):
        """
        Test to update a specific unit manager
        """
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/unit/members/{self.manager_1_1.id}",
                data=json.dumps(
                    {
                        "name": "Updated Unit Manager",
                    }
                ),
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        member = response.json()
        updated_member = self.env["res.partner"].browse(member["id"])
        self.assertEqual(member["name"], "Updated Unit Manager")
        self.assertEqual(updated_member.name, "Updated Unit Manager")

        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Updated Unit Manager",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

    def test_update_unit_wrong_partner(self):
        self.default_fastapi_authenticated_partner = self.collaborator_1_1
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post(
                f"/unit/members/{self.collaborator_1_1.id}",
                data=json.dumps({"name": "New Unit Name"}),
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_delete_unit_membere(self):
        """
        Test to delete a specific unit member
        """
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

        with self._create_test_client() as test_client:
            response: Response = test_client.delete(
                f"/unit/members/{self.collaborator_1_4.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertFalse(self.collaborator_1_4.active)
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.5",
            },
        )

    def test_delete_unit_manager(self):
        """
        Test to delete a specific unit manager
        """
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Manager 1.1",
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

        with self._create_test_client() as test_client:
            response: Response = test_client.delete(
                f"/unit/members/{self.manager_1_1.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(self.manager_1_1.active)
        self.assertEqual(
            set(self.unit_1.member_ids.mapped("name")),
            {
                "Collaborator 1.1",
                "Collaborator 1.2",
                "Collaborator 1.3",
                "Collaborator 1.4",
                "Collaborator 1.5",
            },
        )

    def test_delete_unit_wrong_partner(self):
        self.default_fastapi_authenticated_partner = self.collaborator_1_1
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.delete(
                f"/unit/members/{self.collaborator_1_1.id}",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )
