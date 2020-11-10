# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import unittest
from uuid import uuid4

import requests

from odoo.tools import mute_logger

from .common import ShopinvaderRestCase


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "HTTP case disabled.")
class ShopinvaderControllerCase(ShopinvaderRestCase):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderControllerCase, self).setUp(*args, **kwargs)
        self.url = self.base_url + "/shopinvader/addresses"
        self.partner = self.env.ref("shopinvader.partner_1")
        self.address_1 = self.env.ref("shopinvader.partner_1_address_1")
        self.address_2 = self.env.ref("shopinvader.partner_1_address_2")

    def test_get_addresses_with_correct_api_key_and_partner(self):
        result = requests.get(
            self.url,
            headers={
                "API_KEY": self.backend.auth_api_key_id.key,
                "PARTNER_EMAIL": "osiris@shopinvader.com",
            },
        )
        self.assertEqual(result.status_code, 200)
        data = result.json()["data"]
        self.assertEqual(len(data), 3)
        ids = {x["id"] for x in data}
        expected_ids = {self.partner.id, self.address_1.id, self.address_2.id}
        self.assertEqual(ids, expected_ids)

    def test_get_addresses_with_correct_api_key_and_partner_and_filter(self):
        result = requests.get(
            self.url + "?scope[address_type]=address",
            headers={
                "API_KEY": self.backend.auth_api_key_id.key,
                "PARTNER_EMAIL": "osiris@shopinvader.com",
            },
        )
        self.assertEqual(result.status_code, 200)
        data = result.json()["data"]
        self.assertEqual(len(data), 2)
        ids = {x["id"] for x in data}
        expected_ids = {self.address_1.id, self.address_2.id}
        self.assertEqual(ids, expected_ids)

    @mute_logger(
        "odoo.addons.auth_api_key.models.ir_http",
        "odoo.addons.base_rest.http",
        "odoo.addons.base.models.ir_http",
    )
    def test_get_addresses_with_wrong_api_key(self):
        result = requests.get(
            self.url,
            headers={
                "API_KEY": "WRONG",
                "PARTNER_EMAIL": "osiris@shopinvader.com",
            },
        )
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.json(), {u"code": 403, u"name": u"Forbidden"})

    def test_get_addresses_without_partner(self):
        result = requests.get(
            self.url, headers={"API_KEY": self.backend.auth_api_key_id.key}
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"data": []})

    @mute_logger(
        "odoo.addons.auth_api_key.models.ir_http", "odoo.addons.base_rest.http"
    )
    def test_email_not_exists(self):
        """
        Test the behaviour when the email from header is not found.
        For this case, we use an email who shouldn't exist in the database.
        So it should raise an exception.
        :return:
        """
        # This email shouldn't exist
        email = "%s@random.com" % uuid4()
        headers = {
            "API_KEY": self.backend.auth_api_key_id.key,
            "PARTNER_EMAIL": email,
        }
        res = requests.get(self.url, headers=headers)
        self.assertEqual(res.status_code, 404)

    @mute_logger(
        "odoo.addons.auth_api_key.models.ir_http", "odoo.addons.base_rest.http"
    )
    def test_email_inactive(self):
        """
        Test the behaviour when the email from header is not found.
        For this case, the email address should exist but the related partner
        is inactive. So it should raise an exception.
        :return:
        """
        # This email should exist
        self.partner.write({"active": False})
        headers = {
            "API_KEY": self.backend.auth_api_key_id.key,
            "PARTNER_EMAIL": self.partner.email,
        }
        res = requests.get(self.url, headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_email_not_provided(self):
        """
        Test the behaviour when the email from header is not found.
        For this case, we don't fill the PARTNER_EMAIL so it shouldn't
        have any exception
        :return:
        """
        # Do not provide PARTNER_EMAIL key
        headers = {"API_KEY": self.backend.auth_api_key_id.key}
        requests.get(self.url, headers=headers)
