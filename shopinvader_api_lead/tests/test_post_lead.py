# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers.lead import lead_router


@tagged("post_install", "-at_install")
class TestShopinvaderAPILead(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
                "groups_id": [(6, 0, [])],
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_lead.shopinvader_lead_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_router = lead_router

    def _create_unauthenticated_user_client(self):
        return self._create_test_client(user=self.user_no_rights)

    def test_post_lead(self):
        data = {
            "email": "harry.potter@hogwarts.com",
            "subject": "Question about your site",
            "description": "<p>I would need more info. Can you email me?</p>",
        }
        with self._create_test_client(router=lead_router) as test_client:
            response: Response = test_client.post("/leads", json=data)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )

        lead = self.env["crm.lead"].search([], order="id desc", limit=1)
        self.assertEqual(lead.email_from, data["email"])
        self.assertEqual(lead.name, data["subject"])
        self.assertEqual(lead.description, data["description"])

    def test_post_lead_authenticated_user(self) -> None:
        data = {
            "email": "harry.potter@hogwarts.com",
            "subject": "Question about your site",
            "description": "<p>I would need more info. Can you email me?</p>",
        }
        with (
            self._create_unauthenticated_user_client() as test_client,
            self.assertRaises(AccessError),
        ):
            test_client.post("/leads", json=data)
