# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase
import requests


class ControllerCase(SavepointComponentCase):

    def setUp(self, *args, **kwargs):
        super(ControllerCase, self).setUp(*args, **kwargs)
        self.registry.enter_test_mode()
        self.backend = self.env.ref('shopinvader.backend_1')
        self.base_url = self.env['ir.config_parameter']\
            .get_param('web.base.url')
        self.api_key = self.backend.auth_api_key_id\
            ._get_keychain_account()._get_password()
        self.url = self.base_url + '/shopinvader/addresses'

    def tearDown(self):
        self.registry.leave_test_mode()
        super(ControllerCase, self).tearDown()

    def test_get_addresses_with_correct_api_key_and_partner(self):
        result = requests.get(self.url, headers={
            'API_KEY': self.api_key,
            'PARTNER_EMAIL': 'osiris@my.personal.address.example.com',
            })
        self.assertEqual(result.status_code, 200)
        data = result.json()['data']
        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]['id'],
            self.env.ref('shopinvader.partner_1').id)
        self.assertEqual(
            data[1]['id'],
            self.env.ref('shopinvader.partner_1_address_1').id)

    def test_get_addresses_with_wrong_api_key(self):
        result = requests.get(self.url, headers={
            'API_KEY': 'WRONG',
            'PARTNER_EMAIL': 'osiris@my.personal.address.example.com',
            })
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.json(), {
            u'code': 401,
            u'name': u'Unauthorized',
            u'description': u'<p>Access denied</p>'})

    def test_get_addresses_without_partner(self):
        result = requests.get(self.url, headers={
            'API_KEY': self.api_key,
            })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), [])
