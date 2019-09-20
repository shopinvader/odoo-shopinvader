# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.addons.shopinvader.tests.common import CommonCase


class TestInvoiceService(CommonCase):
    """
    Tests for
    """

    def setUp(self, *args, **kwargs):
        super(TestInvoiceService, self).setUp(*args, **kwargs)
        self.invoice_obj = self.env["account.invoice"]
        self.partner = self.env.ref("base.res_partner_2").copy()
        self.product = self.env.ref("product.product_product_4")
        self.precision = 2
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="invoice")
        with self.work_on_services(
            partner=self.backend.anonymous_partner_id
        ) as work:
            self.service_guest = work.component(usage="invoice")

    def _get_selection_label(self, invoice, field):
        """
        Get the translated label of the invoice selection field
        :param invoice: account.invoice recordset
        :param field: str
        :return: str
        """
        technical_type = invoice[field]
        type_dict = dict(
            invoice._fields.get(field)._description_selection(invoice.env)
        )
        return type_dict.get(technical_type, technical_type)

    def _check_data_content(self, data, invoices):
        """
        Check data based on given invoices
        :param data: list
        :param invoices: account.invoice recordset
        :return: bool
        """
        # To have them into correct order
        invoices = invoices.search(
            [
                ("id", "in", invoices.ids),
                # Invoice must be paid to be in data
                ("state", "in", ["open", "paid"]),
            ]
        )
        self.assertEquals(len(data), len(invoices))
        for current_data, invoice in zip(data, invoices):
            state_label = self._get_selection_label(invoice, "state")
            type_label = self._get_selection_label(invoice, "type")
            self.assertEquals(current_data.get("invoice_id"), invoice.id)
            self.assertEquals(current_data.get("number"), invoice.number)
            self.assertEquals(
                current_data.get("date_invoice"), invoice.date_invoice
            )
            self.assertEquals(current_data.get("state"), state_label)
            self.assertEquals(current_data.get("type"), type_label)
            self.assertEquals(
                current_data.get("amount_total"), invoice.amount_total
            )
            self.assertEquals(
                current_data.get("amount_tax"), invoice.amount_tax
            )
            self.assertEquals(
                current_data.get("amount_untaxed"), invoice.amount_untaxed
            )
            self.assertEquals(current_data.get("amount_due"), invoice.residual)
        return True

    def _create_invoice(
        self, partner=False, inv_type="out_invoice", validate=False
    ):
        """
        Create a new invoice
        :param partner: res.partner
        :param inv_type: str
        :param validate: bool
        :return: stock.invoice recordset
        """
        partner = partner or self.partner
        account = self.product.categ_id.property_account_expense_categ_id
        values = {
            "partner_id": partner.id,
            "partner_shipping_id": partner.id,
            "shopinvader_backend_id": self.backend.id,
            "date_invoice": fields.Date.today(),
            "type": inv_type,
            "invoice_line_ids": [
                (
                    0,
                    False,
                    {
                        "product_id": self.product.id,
                        "quantity": 10,
                        "price_unit": 1250,
                        "account_id": account.id,
                        "name": self.product.display_name,
                    },
                )
            ],
        }
        invoice = self.invoice_obj.create(values)
        if validate:
            invoice.action_invoice_open()
        return invoice

    def test_get_invoice_anonymous(self):
        """
        Test the get on guest mode (using anonymous user).
        It should not return any result, even if the anonymous user has some
        invoices
        :return:
        """
        # Check first without invoice related to the anonymous user
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to the anonymous user
        invoice = self._create_invoice(
            partner=self.backend.anonymous_partner_id, validate=True
        )
        self.assertEquals(
            invoice.partner_id, self.backend.anonymous_partner_id
        )
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        return

    def test_get_invoice_logged(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any invoice.
        But to the second, he should have one.
        :return:
        """
        # Check first without invoice related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to partner
        invoice = self._create_invoice(partner=self.service.partner)
        self.assertEquals(invoice.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoice)
        invoice.action_invoice_open()
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoice)
        return

    def test_get_multi_invoice(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any invoice.
        But to the second, he should have one.
        :return:
        """
        invoice1 = self._create_invoice(
            partner=self.service.partner, validate=True
        )
        invoice2 = self._create_invoice(
            partner=self.service.partner, validate=True
        )
        invoice3 = self._create_invoice(
            partner=self.service.partner, validate=True
        )
        invoice4 = self._create_invoice(partner=self.service.partner)
        invoices = invoice1 | invoice2 | invoice3 | invoice4
        self.assertEquals(invoice1.partner_id, self.service.partner)
        self.assertEquals(invoice2.partner_id, self.service.partner)
        self.assertEquals(invoice3.partner_id, self.service.partner)
        self.assertEquals(invoice4.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoices)
        return
