# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.sign import SignService
from .common import CommonCase


class CustomerCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(CustomerCase, self).setUp(*args, **kwargs)
        templates = self.env['product.template'].search([])
        templates.write({
            'taxes_id': [(6, 0, [self.env.ref('shopinvader.tax_1').id])]})
        with self.backend.work_on(
                model_name='locomotive.backend',
                partner=None,
                shopinvader_session={}) as work:
            self.service = work.component(usage='sign.service')

    def test_create_customer(self):
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
        res = self.service.create(data)['data']
        partner = self.env['res.partner'].browse(res['id'])
        self.assertEqual(partner.email, data['email'])
        self.assertEqual(
            partner.shopinvader_bind_ids.external_id,
            data['external_id'])
        for key in data:
            if key == 'external_id':
                continue
            elif key == 'country_id':
                self.assertEqual(partner[key].id, data[key])
            else:
                self.assertEqual(partner[key], data[key])
        self.assertEqual(
            partner.shopinvader_bind_ids.role_id,
            self.env.ref('shopinvader.role_1'))

    def test_create_customer_business_role(self):
        data = {
            'email': 'business@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            'vat': 'BE0477472701',
            }
        res = self.service.create(data)['data']
        partner = self.env['res.partner'].browse(res['id'])
        # Note for now we do not have automatic rule to
        # set a specific pricelist depending on vat number
        # so we set it manually
        partner.property_product_pricelist =\
            self.env.ref('shopinvader.pricelist_1').id
        self.assertEqual(
            partner.shopinvader_bind_ids.role_id,
            self.env.ref('shopinvader.role_2'))
        self.assertEqual(partner.is_company, True)

    def test_create_customer_exclude_role(self):
        data = {
            'email': 'export@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.us').id,
            }
        res = self.service.create(data)['data']
        self.partner = self.env['res.partner'].browse(res['id'])
        self.assertEqual(
            self.partner.shopinvader_bind_ids.role_id,
            self.env.ref('shopinvader.role_3'))

    def test_address_type(self):
        partner = self.env.ref('shopinvader.partner_1')
        self.assertEqual(partner.address_type, 'profile')
        address = self.env.ref('shopinvader.partner_1_address_1')
        self.assertEqual(address.address_type, 'address')

    def test_update_address_type(self):
        data = {
            'email': 'address@customer.example.com',
            'name': 'Address',
            'country_id': self.env.ref('base.fr').id,
            }
        partner = self.env['res.partner'].create(data)
        self.assertEqual(partner.address_type, 'profile')
        data = {
            'email': 'parent@customer.example.com',
            'name': 'Parent',
            'country_id': self.env.ref('base.fr').id,
            }
        parent = self.env['res.partner'].create(data)
        partner.parent_id = parent.id
        self.assertEqual(partner.address_type, 'address')
