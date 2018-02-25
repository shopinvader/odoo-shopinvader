# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import (
    SavepointComponentCase,
    new_rollbacked_env)
import requests
from odoo.addons.component.core import (
    _get_addon_name,
)


class RegistryMixin(object):

    @classmethod
    def setUpRegistry(cls):
        with new_rollbacked_env() as env:
            service_registration = env['rest.service.registration']
            # build the registry of every installed addons
            services_registry = service_registration._init_global_registry()
            cls._services_registry = services_registry
            # ensure that we load only the services of the 'installed'
            # modules, not 'to install', which means we load only the
            # dependencies of the tested addons, not the siblings or
            # chilren addons
            service_registration.build_registry(
                services_registry, states=('installed',))
            # build the services of the current tested addon
            current_addon = _get_addon_name(cls.__module__)
            env['rest.service.registration'].load_services(
                current_addon, services_registry)


class ControllerCase(SavepointComponentCase, RegistryMixin):

    @classmethod
    def setUpClass(cls):
        super(ControllerCase, cls).setUpClass()
        cls.setUpRegistry()

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
        self.assertEqual(result.json(), [])
