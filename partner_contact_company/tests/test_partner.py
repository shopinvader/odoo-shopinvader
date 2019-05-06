# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestPartnerName(common.TransactionCase):
    def test_name(self):
        partner = self.env.ref("partner_contact_company.partner_test_name")
        self.assertEqual(partner.name, "Test name")
        self.assertEqual(partner.company, False)
        self.assertEqual(partner.contact_name, "Test name")

    def test_company(self):
        partner = self.env.ref("partner_contact_company.partner_test_company")
        self.assertEqual(partner.name, "Test company")
        self.assertEqual(partner.company, "Test company")
        self.assertEqual(partner.contact_name, False)

    def test_contact_name(self):
        partner = self.env.ref(
            "partner_contact_company.partner_test_contact_name"
        )
        self.assertEqual(partner.name, "Test contact name")
        self.assertEqual(partner.company, False)
        self.assertEqual(partner.contact_name, "Test contact name")

    def test_company_contact_name(self):
        partner = self.env.ref(
            "partner_contact_company.partner_test_company_contact_name"
        )
        self.assertEqual(partner.name, "Company, Contact name")
        self.assertEqual(partner.company, "Company")
        self.assertEqual(partner.contact_name, "Contact name")
