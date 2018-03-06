# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
import logging
_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestCustomer(CommonCase):

    def setUp(self, *args, **kwargs):
        super(TestCustomer, self).setUp(*args, **kwargs)
        self.data = {
            'email': 'new@customer.example.com',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country': {'id': self.env.ref('base.fr').id},
            }
        with self.work_on_services(
                partner=None,
                shopinvader_session=self.shopinvader_session) as work:
            self.service = work.component(usage='customer')

    def test_create_customer(self):
        self.data['external_id'] = 'D5CdkqOEL'
        res = self.service.dispatch('create', params=self.data)['data']
        partner = self.env['res.partner'].browse(res['id'])
        self.assertEqual(partner.email, self.data['email'])
        self.assertEqual(
            partner.shopinvader_bind_ids.external_id,
            self.data['external_id'])
        for key in self.data:
            if key == 'external_id':
                continue
            elif key == 'country':
                self.assertEqual(partner.country_id.id, self.data[key]['id'])
            else:
                self.assertEqual(partner[key], self.data[key])

    def test_address_type(self):
        partner = self.env.ref('shopinvader.partner_1')
        self.assertEqual(partner.address_type, 'profile')
        address = self.env.ref('shopinvader.partner_1_address_1')
        self.assertEqual(address.address_type, 'address')

    def test_update_address_type(self):
        data = {
            'email': 'address@customer.example.com',
            'name': 'Address',
            'country': {'id': self.env.ref('base.fr').id},
            }
        partner = self.env['res.partner'].create(data)
        self.assertEqual(partner.address_type, 'profile')
        data = {
            'email': 'parent@customer.example.com',
            'name': 'Parent',
            'country': {'id': self.env.ref('base.fr').id},
            }
        parent = self.env['res.partner'].create(data)
        partner.parent_id = parent.id
        self.assertEqual(partner.address_type, 'address')

    def _create_customer_in_odoo(self, data, external_id):
        partner = self.env['res.partner'].create(data)
        self._init_job_counter()
        shopinvader_partner = self.env['shopinvader.partner'].create({
            'record_id': partner.id,
            'backend_id': self.backend.id,
            })
        self._check_nbr_job_created(1)
        base_url = self.backend.location + '/locomotive/api/v3'
        with requests_mock.mock() as m:
            m.post(
                base_url + '/tokens.json',
                json={'token': u'744cfcfb3cd3'})
            m.post(
                base_url + '/content_types/customers/entries',
                json={'_id': external_id})
            self._perform_created_job()
        return shopinvader_partner

    def test_create_customer_from_odoo(self):
        shop_partner = self._create_customer_in_odoo(
            self.data, u'5a953d6aae1c744cfcfb3cd3')
        self.assertEqual(
            shop_partner.external_id, u'5a953d6aae1c744cfcfb3cd3')

    def test_delete_customer_from_odoo(self):
        shop_partner = self._create_customer_in_odoo(
            self.data, u'5a953d6aae1c744cfcfb3cd3')
        self._init_job_counter()
        shop_partner.unlink()
        self._check_nbr_job_created(1)
        base_url = self.backend.location + '/locomotive/api/v3'
        with requests_mock.mock() as m:
            m.post(
                base_url + '/tokens.json',
                json={'token': u'744cfcfb3cd3'})
            m.delete(
                base_url +
                '/content_types/customers/entries/5a953d6aae1c744cfcfb3cd3',
                json={})
            self._perform_created_job()
