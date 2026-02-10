# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import partial

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi.dependencies import fastapi_endpoint

from ..routers.mass_mailing import mass_mailing_router


class CommonMassMailingCase(FastAPITransactionCase):
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
                                "shopinvader_api_mass_mailing."
                                "shopinvader_mass_mailing_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_router = mass_mailing_router
        cls.ml = cls.env["mailing.list"].create(
            {
                "name": "Test Mailing List",
            }
        )
        cls.endpoint = cls.env["fastapi.endpoint"].create(
            {
                "name": "Test Endpoint",
                "app": "demo",
                "demo_auth_method": "http_basic",
                "root_path": "/test-endpoint",
                "user_id": cls.default_fastapi_running_user.id,
                "mailing_list_id": cls.ml.id,
            }
        )

    def _create_test_client(self, **kwargs):
        kwargs.setdefault(
            "dependency_overrides",
            {fastapi_endpoint: partial(lambda a: a, self.endpoint)},
        )
        return super()._create_test_client(**kwargs)
