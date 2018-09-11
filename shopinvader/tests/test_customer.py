# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
import logging
_logger = logging.getLogger(__name__)


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
            'is_company': False,
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
