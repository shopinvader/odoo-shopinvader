# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import contextlib

from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.addons.website.tools import MockRequest

from .common import TestMultiUserCommon


class TestMultiUserServiceCtx(TestMultiUserCommon):
    """Test interaction with service component context.
    """

    # TODO: would be nice to have this in core module (or base_rest)
    # to allow full testing of the service stack w/out using HttpTestCase
    @contextlib.contextmanager
    def _get_mocked_request(self, partner):
        with MockRequest(self.env) as mocked_request:
            mocked_request.httprequest.environ.update(
                {"HTTP_PARTNER_EMAIL": partner.email}
            )
            mocked_request.auth_api_key_id = self.backend.auth_api_key_id.id
            yield mocked_request

    def test_partner_ctx_default_multi_disabled(self):
        self.backend.customer_multi_user = False
        ctrl = InvaderController()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.user_binding.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.user_binding.record_id)
        self.assertEqual(ctx["partner"], self.user_binding.record_id)

    def test_partner_ctx_default_multi_enabled(self):
        ctrl = InvaderController()
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
        ctrl = InvaderController()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.user_binding.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.user_binding.record_id)
        self.assertEqual(ctx["partner"], self.user_binding.record_id)
