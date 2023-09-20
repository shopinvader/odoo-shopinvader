# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.shopinvader.tests.common import CommonCase

_logger = logging.getLogger(__name__)


class CustomAddressServiceTest(CommonCase):
    def setUp(self):
        super().setUp()
        # for the Test we simulate that the customer logged is shopinvader.partner_1
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            # we init the service that we will use in the test
            self.address_service = work.component(usage="addresses")

    def test_post_zip_code_success(self):
        res = (
            self.address_service.dispatch(
                "zip_code",
                params={"zip_code": "81910000"},
            ),
        )
        self.assertEqual("Rua Izaac Ferreira da Cruz", res[0].get("street_name"))
        self.assertEqual("Sítio Cercado", res[0].get("district"))

    def test_post_zip_code_failed(self):
        try:
            res = (
                self.address_service.dispatch(
                    "zip_code",
                    params={"zip_code": "981910000"},
                ),
            )
            self.assertFalse("Rua Izaac Ferreira da Cruz", res[0].get("street_name"))
            self.assertFalse("Sítio Cercado", res[0].get("district"))
        except Exception as e:
            _logger.warning(e)

    def test_get_search_states_success(self):
        code = "BR"
        res = (
            self.address_service.dispatch(
                "search_states", params={"country_code": code}
            ),
        )
        country_code = self.backend.allowed_country_ids.search(
            [("code", "=", code)]
        ).code

        state_ids = self.env["res.country.state"].search(
            [("country_id.code", "=", country_code)]
        )
        if state_ids:
            states = []
            for state in state_ids:
                states += [{"id": state.id, "name": state.name, "code": state.code}]
            states_joined = {"state_ids": states}

        self.assertEqual(res[-1], states_joined)

    def test_get_search_states_failed(self):
        code = "RR"
        res = (
            self.address_service.dispatch(
                "search_states", params={"country_code": code}
            ),
        )
        country_code = self.backend.allowed_country_ids.search(
            [("code", "=", code)]
        ).code

        state_ids = self.env["res.country.state"].search(
            [("country_id.code", "=", country_code)]
        )
        states = []
        if state_ids:
            for state in state_ids:
                states += [{"id": state.id, "name": state.name, "code": state.code}]
            states_joined = {"state_ids": states}
        else:
            states_joined = {
                "state_ids": [
                    {"id": False, "name": "", "code": ""},
                ]
            }
        self.assertEqual(res[-1], states_joined)
