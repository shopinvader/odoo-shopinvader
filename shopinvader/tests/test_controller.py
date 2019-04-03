# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest
from .common import ShopinvaderRestCase
import requests

from odoo.addons.server_environment import serv_config
from odoo.tools import mute_logger


@unittest.skipIf(
    ShopinvaderRestCase.AUTH_API_KEY_NAME not in serv_config.sections(),
    "You must define an auth_api_key section '%s' into your configuration "
    "to run controller tests" % ShopinvaderRestCase.AUTH_API_KEY_NAME)
class ShopinvaderControllerCase(ShopinvaderRestCase):

    def setUp(self, *args, **kwargs):
        super(ShopinvaderControllerCase, self).setUp(*args, **kwargs)
        self.url = self.base_url + '/shopinvader/addresses'
        self.partner = self.env.ref('shopinvader.partner_1')
        self.address_1 = self.env.ref('shopinvader.partner_1_address_1')
        self.address_2 = self.env.ref('shopinvader.partner_1_address_2')

    def test_get_addresses_with_correct_api_key_and_partner(self):
        result = requests.get(self.url, headers={
            'API_KEY': self.api_key,
            'PARTNER_EMAIL': 'osiris@shopinvader.com',
            })
        self.assertEqual(result.status_code, 200)
        data = result.json()['data']
        self.assertEqual(len(data), 3)
        ids = set([x['id'] for x in data])
        expected_ids = set([
            self.partner.id, self.address_1.id, self.address_2.id])
        self.assertEqual(ids, expected_ids)

    def test_get_addresses_with_correct_api_key_and_partner_and_filter(self):
        result = requests.get(
            self.url + '?scope[address_type]=address',
            headers={
                'API_KEY': self.api_key,
                'PARTNER_EMAIL': 'osiris@shopinvader.com',
            })
        self.assertEqual(result.status_code, 200)
        data = result.json()['data']
        self.assertEqual(len(data), 2)
        ids = set([x['id'] for x in data])
        expected_ids = set([self.address_1.id, self.address_2.id])
        self.assertEqual(ids, expected_ids)

    @mute_logger('odoo.addons.auth_api_key.models.ir_http',
                 'odoo.addons.base_rest.http')
    def test_get_addresses_with_wrong_api_key(self):
        result = requests.get(self.url, headers={
            'API_KEY': 'WRONG',
            'PARTNER_EMAIL': 'osiris@shopinvader.com',
            })
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.json(), {
            u'code': 403,
            u'name': u'Forbidden'})

    def test_get_addresses_without_partner(self):
        result = requests.get(self.url, headers={
            'API_KEY': self.api_key,
            })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {'data': []})
