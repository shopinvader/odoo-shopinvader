# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.addons.fastapi.tests.common import FastAPITransactionCase


class CommonFastAPIEndpointCase(FastAPITransactionCase):
    @classmethod
    def setUpEndpoint(cls, endpoint, api_user=None, default_partner=None):
        cls.endpoint = cls.env.ref(endpoint) if isinstance(endpoint, str) else endpoint

        cls.env = cls.env(
            context=dict(
                **cls.env.context,
                # Since env often comes from the authenticated_partner which
                # doesn't use odoo_env dependency in tests we need to set
                # the context explicitly for all the cases:
                **cls.endpoint._get_app_context(),
            )
        )

        # Set up endpoint app
        cls.default_fastapi_app = cls.endpoint._get_app()

        # Set up endpoint dependency overrides except for partners
        # (These are set by default_fastapi_authenticated_partner or directly
        # partner in _create_test_client)
        cls.default_fastapi_dependency_overrides = {
            k: v
            for k, v in cls.default_fastapi_app.dependency_overrides.items()
            if k.__name__
            not in (
                "authenticated_partner_impl",
                "optionally_authenticated_partner_impl",
            )
        }

        if api_user:
            api_user = cls.env.ref(api_user) if isinstance(api_user, str) else api_user
            cls.default_fastapi_running_user = api_user

        if default_partner:
            cls.partner = (
                cls.env.ref(default_partner)
                if isinstance(default_partner, str)
                else default_partner
            )
            cls.default_fastapi_authenticated_partner = cls.partner

    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()

        from .models import (
            RouterHelperTestBase,
            RouterHelperTestContext,
            RouterHelperTestModelBound,
            RouterHelperTestModelBoundNoDomain,
            RouterHelperTestRelations,
        )

        self.loader.update_registry(
            (
                RouterHelperTestBase,
                RouterHelperTestContext,
                RouterHelperTestModelBound,
                RouterHelperTestModelBoundNoDomain,
                RouterHelperTestRelations,
            )
        )

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()
