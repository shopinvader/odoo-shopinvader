# Copyright 2021 ForgeFlow S.A. (https://forgeflow.com)
# Copyright 2018 Akretion (https://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<https://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
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


class TestShopinvaderPartner(CommonShopinvaderPartner):
    def _get_shopinvader_partner(self, shopinvader_partner, external_id):
        with requests_mock.mock() as m:
            m.post(
                self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"}
            )
            # Request to modify / fake json arg
            res = m.put(
                self.base_url
                + "/content_types/customers/entries/"
                + external_id,
                json={"test": 1},
            )
            self._perform_created_job()
            return shopinvader_partner, res.request_history[0].json()

    def test_can_manage_users_create_shopinvader_partner_from_odoo(self):

        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        can_manage_users = params.get("content_entry").get("can_manage_users")
        self.assertEquals("can_manage_users", can_manage_users)
        self._init_job_counter()
        shop_partner.record_id.write({"can_manage_users": True})
        self._check_nbr_job_created(1)
        partner, params = self._get_shopinvader_partner(
            shop_partner, u"5a953d6aae1c744cfcfb3cd3"
        )
        can_manage_users = params.get("content_entry").get("can_manage_users")
        self.assertEquals("can_manage_users", can_manage_users)
