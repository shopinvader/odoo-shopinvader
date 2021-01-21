# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields
from odoo.exceptions import AccessError

from .common import LocoCommonCase

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class CommonShopinvaderPartner(LocoCommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.data = {
            "email": "new@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country_id": self.env.ref("base.fr").id,
        }

    def _create_shopinvader_partner(self, data, external_id):
        partner = self.env["res.partner"].create(data)
        self._init_job_counter()
        shopinvader_partner = self.env["shopinvader.partner"].create(
            {"record_id": partner.id, "backend_id": self.backend.id}
        )
        # The creation of a shopinvader partner into odoo must trigger
        # the creation of a user account into locomotive
        self._check_nbr_job_created(1)
        with requests_mock.mock() as m:
            m.post(self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
            res = m.post(
                self.base_url + "/content_types/customers/entries",
                json={"_id": external_id},
            )
            self._perform_created_job()
            return shopinvader_partner, res.request_history[0].json()


class TestShopinvaderPartner(CommonShopinvaderPartner):
    def test_create_shopinvader_partner_from_odoo(self):
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        self.assertEqual(
            params,
            {
                u"content_entry": {
                    u"role": u"default",
                    u"email": u"new@customer.example.com",
                    u"name": u"Purple",
                }
            },
        )
        self.assertEqual(shop_partner.external_id, u"5a953d6aae1c744cfcfb3cd3")

    def test_delete_shopinvader_partner_from_odoo(self):
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        self._init_job_counter()
        shop_partner.unlink()
        # The deletion of a shopinvader into odoo must trigger the deletion
        # of a user account into locomotive
        self._check_nbr_job_created(1)
        with requests_mock.mock() as m:
            m.post(self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
            m.delete(
                self.base_url
                + "/content_types/customers/entries/5a953d6aae1c744cfcfb3cd3",
                json={},
            )
            self._perform_created_job()

    def test_update_shopinvader_partner_from_odoo(self):
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        self._init_job_counter()
        partner = shop_partner.record_id
        partner.write({"name": "TEST"})
        # As we updated a field to export, a job should be created
        self._check_nbr_job_created(1)

    def test_no_update_shopinvader_partner_from_odoo(self):
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        self._init_job_counter()
        partner = shop_partner.record_id
        partner.write({"city": "TEST"})
        # As we did not updated a field to export, no job should be created
        self._check_nbr_job_created(0)

    def test_binding_access_rights(self):
        shop_partner, params = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )
        demo_user_id = self.ref("base.user_demo")
        self._init_job_counter()
        partner = shop_partner.record_id.with_user(demo_user_id)
        # demo user has no write access on shopinvader_partner model
        with self.assertRaises(AccessError):
            shop_partner.with_user(demo_user_id).write(
                {"sync_date": fields.Datetime.now()}
            )

        # demo user triggers an export to Locomotive
        partner.write({"name": "TEST"})
        # As we updated a field to export, a job should be created
        self._check_nbr_job_created(1)
        with requests_mock.mock() as m:
            m.post(self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
            m.put(
                self.base_url
                + "/content_types/customers/entries/5a953d6aae1c744cfcfb3cd3",
                json={},
            )
            # export ran as demo user even if no access on shopinvader_partner
            self._perform_created_job()

    def test_get_binding_to_export(self):
        """
        Ensure the function _get_binding_to_export() correctly return
        shopinvader.partner related to current partner.
        :return:
        """
        shop_partner = self._create_shopinvader_partner(
            self.data, u"5a953d6aae1c744cfcfb3cd3"
        )[0]
        partner = shop_partner.record_id
        self.assertEqual(partner._get_binding_to_export(), shop_partner)
        return
