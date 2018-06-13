# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ShopinvaderRestCase
import requests


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
        ids = [x['id'] for x in data]
        self.assertEqual(
            ids, [self.partner.id, self.address_1.id, self.address_2.id])

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
        ids = [x['id'] for x in data]
        self.assertEqual(ids, [self.address_1.id, self.address_2.id])

    def test_get_addresses_with_wrong_api_key(self):
        result = requests.get(self.url, headers={
            'API_KEY': 'WRONG',
            'PARTNER_EMAIL': 'osiris@shopinvader.com',
            })
        self.assertEqual(result.status_code, 403)
        self.assertEqual(result.json(), {
            u'code': 403,
            u'name': u'Forbidden',
            u'description': u'<p>Access denied</p>'})

    def test_get_addresses_without_partner(self):
        result = requests.get(self.url, headers={
            'API_KEY': self.api_key,
            })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {'data': []})
