# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import contextlib

from odoo.addons.component.core import Component
from odoo.addons.website.tools import MockRequest

from .common import TestMultiUserCommon


class TestMultiUserServiceCtx(TestMultiUserCommon):
    """Test interaction with service component context."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create a context provider retrieving the partner
        # from the HTTP header HTTP_PARTNER_EMAIL
        # The way the user is retrieved from the request depends on
        # the authentication system used... here we emulate the way
        # auth_api_key works when shopinvdaer_auth_api_key is installed
        class TestShopinvaderServiceContextProvider(Component):
            _inherit = "shopinvader.service.context.provider"

            def _get_shopinvader_partner(self):
                headers = self.request.httprequest.environ
                partner_email = headers.get("HTTP_PARTNER_EMAIL")
                backend = self._get_backend()
                return self._find_partner(backend, partner_email)

        TestShopinvaderServiceContextProvider._build_component(cls._components_registry)

    # TODO: would be nice to have this in core module (or base_rest)
    # to allow full testing of the service stack w/out using HttpTestCase
    @contextlib.contextmanager
    def _get_mocked_request(self, partner):
        with MockRequest(self.env) as mocked_request:
            mocked_request.httprequest.environ.update(
                {
                    "HTTP_PARTNER_EMAIL": partner.email,
                    "HTTP_WEBSITE_UNIQUE_KEY": self.backend.website_unique_key,
                }
            )
            yield mocked_request

    def test_partner_ctx_default_multi_disabled(self):
        self.backend.customer_multi_user = False
        ctrl = self._ShopinvaderControllerTest()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.user_binding.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.user_binding.record_id)
        self.assertEqual(ctx["partner"], self.user_binding.record_id)

    def test_partner_ctx_default_multi_enabled(self):
        ctrl = self._ShopinvaderControllerTest()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.user_binding.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.user_binding.record_id)
        self.assertEqual(ctx["partner"], self.user_binding.main_partner_id)

    def test_partner_ctx_default_multi_enabled_user_partner(self):
        self.backend.multi_user_profile_policy = "record_id"
        ctrl = self._ShopinvaderControllerTest()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.user_binding.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.user_binding.record_id)
        self.assertEqual(ctx["partner"], self.user_binding.record_id)
