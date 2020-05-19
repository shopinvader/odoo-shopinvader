# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
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


class TestShopinvaderPartner(CommonShopinvaderPartner):
    def setUp(self):
        super(TestShopinvaderPartner, self).setUp()

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

    def test_profile_create_shopinvader_partner_from_odoo(self):

        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        role = params.get("content_entry").get("role")
        self.assertEquals("default", role)
        # Use Sale profile from now
        self._init_job_counter()
        self.backend.pricelist_id = False
        self.backend.use_sale_profile = True
        # Used to restart export job
        shop_partner.record_id.write({"vat": "BE0477472701"})
        self._check_nbr_job_created(1)
        partner, params = self._get_shopinvader_partner(
            shop_partner, u"5a953d6aae1c744cfcfb3cd3"
        )
        role = params.get("content_entry").get("role")
        self.assertEquals("public_tax_inc", role)

    def test_profile_no_fiscal_pos(self):
        pricelist = self.env["product.pricelist"].create(
            {"name": "TEST profile"}
        )
        profile = self.env["shopinvader.sale.profile"].create(
            {
                "code": "NoFPos",
                "pricelist_id": pricelist.id,
                "backend_id": self.env.ref("shopinvader.backend_1").id,
            }
        )
        self.data.update(
            {
                "property_product_pricelist": pricelist.id,
                "property_account_position_id": False,
                "country_id": False,
            }
        )
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953dmpefe1c744cfcfb3cd3"
        )

        self.assertEqual(shop_partner.property_product_pricelist, pricelist)
        self.backend.pricelist_id = False
        self.backend.use_sale_profile = True
        partner, params = self._get_shopinvader_partner(
            shop_partner, u"5a953dmpefe1c744cfcfb3cd3"
        )
        role = params.get("content_entry").get("role")
        self.assertEquals(role, profile.code)
