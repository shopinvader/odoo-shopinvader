# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.customer import CustomerService
from .common import CommonCase


class CustomerCase(CommonCase):

    def test_create_customer(self):
        service = self._get_service(CustomerService, None)
        data = {
            'email': 'new@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            }
        res = service.create(data)
        partner = self.env['res.partner'].browse(res['id'])
        self.assertEqual(partner.email, data['email'])
        self.assertEqual(
            partner.locomotive_bind_ids.external_id,
            data['external_id'])
        for key in data:
            if key == 'external_id':
                continue
            elif key == 'country_id':
                self.assertEqual(partner[key].id, data[key])
            else:
                self.assertEqual(partner[key], data[key])
