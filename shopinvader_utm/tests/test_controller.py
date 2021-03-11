# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import contextlib

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.website.tools import MockRequest

from ..controllers.main import UtmController


class UtmControllerCase(CommonCase):
    @contextlib.contextmanager
    def _get_mocked_request(self, partner):
        with MockRequest(self.env) as mocked_request:
            mocked_request.httprequest.environ.update(
                {"HTTP_PARTNER_EMAIL": partner.email}
            )
            mocked_request.httprequest.environ.update(
                {
                    "HTTP_UTM_CAMPAIGN": "Christmas Special",
                    "HTTP_UTM_MEDIUM": "Facebook",
                    "HTTP_UTM_SOURCE": "Twitter",
                    "HTTP_UTM_TEST": "Test",
                }
            )
            mocked_request.auth_api_key_id = self.backend.auth_api_key_id.id
            yield mocked_request

    def test_utm_headers(self):
        ctrl = UtmController()
        partner = self.env.ref("shopinvader.partner_1")
        with self._get_mocked_request(partner):
            ctx = ctrl._get_component_context()
        self.assertEqual(len(ctx["utm"]), 3)
        self.assertEqual(ctx["utm"]["campaign"], "Christmas Special")
        self.assertEqual(ctx["utm"]["medium"], "Facebook")
        self.assertEqual(ctx["utm"]["source"], "Twitter")
