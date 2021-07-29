# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.shopinvader_locomotive.tests.test_shopinvader_partner import (
    CommonShopinvaderPartner,
)

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestShopinvaderPasswordSync(CommonShopinvaderPartner):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["shopinvader.partner"].create(
            {
                "name": "John",
                "email": "john@test.com",
                "backend_id": cls.backend.id,
                "external_id": "john",
            }
        )
        cls.partner2 = cls.env["shopinvader.partner"].create(
            {
                "name": "Mike",
                "email": "mike@test.com",
                "backend_id": cls.backend.id,
                "external_id": "mike",
            }
        )

    def test_change_pwd(self):
        partner_binding = self.partner2
        self._init_job_counter()
        new_pwd = "something-very-secret"
        partner_binding.password = new_pwd
        self._check_nbr_job_created(1)

        with requests_mock.mock() as m:
            m.post(self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
            m.put(
                self.base_url
                + "/content_types/customers/entries/"
                + partner_binding.external_id,
                json={},
            )
            # export ran as demo user even if no access on shopinvader_partner
            self._perform_created_job()
            data = m.request_history[1].json()["content_entry"]
            self.assertEqual(data["password"], new_pwd)
