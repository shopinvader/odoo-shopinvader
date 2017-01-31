# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment
from ..services.contact import ContactService
from werkzeug.exceptions import Forbidden


class ContactCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(ContactCase, self).setUp(*args, **kwargs)
        self.backend = self.env.ref('connector_locomotivecms.backend_1')
        session = ConnectorSession.from_env(self.env)
        env = get_environment(session, 'res.partner', self.backend.id)
        self.service = env.get_connector_unit(ContactService)
        self.partner = self.env.ref('shoptor.partner_1')
        self.contact = self.env.ref('shoptor.partner_1_contact_1')
        self.contact_params = {
            'partner_email': self.partner.email,
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
        contact = self.service.create(self.contact_params)
        contact = self.env['res.partner'].browse(contact['id'])
        self.assertEqual(contact.parent_id, self.partner)
        self.check_data(contact, self.contact_params)

    def test_update_contact(self):
        params = self.contact_params
        params['id'] = self.contact.id
        res = self.service.update(params)
        contact = self.env['res.partner'].browse(res['id'])
        self.assertEqual(contact.parent_id, self.partner)
        self.check_data(contact, params)

    def test_update_main_contact(self):
        params = self.contact_params
        params['id'] = self.partner.id
        res = self.service.update(params)
        contact = self.env['res.partner'].browse(res['id'])
        self.assertEqual(contact, self.partner)
        self.check_data(contact, params)

    def test_read_contact_profile(self):
        res = self.service.list({
            'partner_email': self.partner.email,
            'contact_type': 'profile'})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], self.partner.id)

    def test_read_contact_address(self):
        res = self.service.list({
            'partner_email': self.partner.email,
            'contact_type': 'address'})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['id'], self.contact.id)

    def test_read_contact_all(self):
        res = self.service.list({'partner_email': self.partner.email})
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['id'], self.partner.id)
        self.assertEqual(res[1]['id'], self.contact.id)

    def test_delete_contact(self):
        contact_id = self.contact.id
        self.service.delete({
            'partner_email': self.partner.email,
            'id': contact_id,
            })
        contact = self.env['res.partner'].search([('id', '=', contact_id)])
        self.assertEqual(len(contact), 0)
        partner = self.env['res.partner'].search([
            ('id', '=', self.partner.id)])
        self.assertEqual(len(partner), 1)

    def test_delete_main_contact(self):
        with self.assertRaises(Forbidden):
            self.service.delete({
                'partner_email': self.partner.email,
                'id': self.partner.id,
                })
