# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.contact import ContactService
from .common import CommonCase
from werkzeug.exceptions import Forbidden


class ContactCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(ContactCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('shopinvader.partner_1')
        self.service = self._get_service(ContactService, self.partner)
        self.contact = self.env.ref('shopinvader.partner_1_contact_1')
        self.contact_params = {
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            }

    def check_data(self, contact, data):
        for key in data:
            if key == 'partner_email':
                continue
            elif key == 'country_id':
                self.assertEqual(contact[key].id, data[key])
            else:
                self.assertEqual(contact[key], data[key])

    def test_add_contact(self):
        contact_ids = [
            contact['id']
            for contact in self.service.get({})['data']]
        contact_list = self.service.create(self.contact_params)['data']
        for contact in contact_list:
            if contact['id'] not in contact_ids:
                created_contact = contact
        self.assertIsNotNone(created_contact)
        contact = self.env['res.partner'].browse(created_contact['id'])
        self.assertEqual(contact.parent_id, self.partner)
        self.check_data(contact, self.contact_params)

    def test_update_contact(self):
        params = self.contact_params
        params['id'] = self.contact.id
        self.service.update(params)
        self.assertEqual(self.contact.parent_id, self.partner)
        self.check_data(self.contact, params)

    def test_update_main_contact(self):
        params = self.contact_params
        params['id'] = self.partner.id
        self.service.update(params)
        self.check_data(self.partner, params)

    def test_read_contact_profile(self):
        res = self.service.get({
            'domain': {'contact_type': 'profile'},
            })['data']
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], self.partner.id)

    def test_read_contact_address(self):
        res = self.service.get({
            'domain': {'contact_type': 'address'},
            })['data']
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], self.contact.id)

    def test_read_contact_all(self):
        res = self.service.get({})['data']
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['id'], self.partner.id)
        self.assertEqual(res[1]['id'], self.contact.id)

    def test_delete_contact(self):
        contact_id = self.contact.id
        self.service.delete({'id': contact_id})
        contact = self.env['res.partner'].search([('id', '=', contact_id)])
        self.assertEqual(len(contact), 0)
        partner = self.env['res.partner'].search([
            ('id', '=', self.partner.id)])
        self.assertEqual(len(partner), 1)

    def test_delete_main_contact(self):
        with self.assertRaises(Forbidden):
            self.service.delete({
                'id': self.partner.id,
                })
