# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.shopinvader.tests.common import CommonCase


class CommonInvoiceCase(CommonCase):
    """
    Common for invoice service
    """

    def setUp(self, *args, **kwargs):
        super(CommonInvoiceCase, self).setUp(*args, **kwargs)
        self.invoice_obj = self.env["account.move"]
        self.journal_obj = self.env["account.journal"]
        self.register_payments_obj = self.env["account.payment.register"]
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.partner = self.env.ref("shopinvader.partner_1")
        self.partner2 = self.env.ref("shopinvader.partner_2")
        self.product = self.env.ref("product.product_product_4")
        self.bank_journal_euro = self.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        self.precision = 2
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="invoices")
        with self.work_on_services(partner=self.backend.anonymous_partner_id) as work:
            self.service_guest = work.component(usage="invoice")

    def _check_data_content(self, data, invoices):
        """
        Check data based on given invoices
        :param data: list
        :param invoices: account.move recordset
        :return: bool
        """
        # To have them into correct order
        invoices = invoices.search([("id", "in", invoices.ids)])
        self.assertEqual(len(data), len(invoices))
        for current_data, invoice in zip(data, invoices):
            payment_state_label = self._get_selection_label(invoice, "payment_state")
            state_label = self._get_selection_label(invoice, "state")
            type_label = self._get_selection_label(invoice, "move_type")
            self.assertEqual(current_data.get("invoice_id"), invoice.id)
            self.assertEqual(current_data.get("number"), invoice.payment_reference)
            self.assertEqual(
                current_data.get("date_invoice"),
                fields.Date.to_string(invoice.invoice_date),
            )
            self.assertEqual(
                current_data.get("state"),
                "open" if invoice.state == "posted" else invoice.state,
            )
            self.assertEqual(current_data.get("payment_state"), invoice.payment_state)
            self.assertEqual(current_data.get("type"), invoice.move_type)
            self.assertEqual(current_data.get("state_label"), state_label)
            self.assertEqual(
                current_data.get("payment_state_label"), payment_state_label
            )
            self.assertEqual(current_data.get("type_label"), type_label)
            self.assertEqual(current_data.get("amount_total"), invoice.amount_total)
            self.assertEqual(
                current_data.get("amount_total_signed"),
                invoice.amount_total_signed,
            )
            self.assertEqual(current_data.get("amount_tax"), invoice.amount_tax)
            self.assertEqual(current_data.get("amount_untaxed"), invoice.amount_untaxed)
            self.assertEqual(
                current_data.get("amount_untaxed_signed"),
                invoice.amount_total_signed,
            )
            self.assertEqual(current_data.get("amount_due"), invoice.amount_residual)
        return True

    def _confirm_and_invoice_sale(self, sale, validate=True, payment=True):
        """
        Confirm the given SO and create an invoice.
        Can also make the payment if payment parameter is True
        :param sale: sale.order recordset
        :param validate: bool
        :param payment: bool
        :return: account.move
        """
        sale.action_confirm()
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice = sale._create_invoices()
        if validate:
            invoice._post()
            if payment:
                self._make_payment(invoice)
        return invoice

    def _make_payment(self, invoice, journal=False, amount=False):
        """
        Make payment for given invoice
        :param invoice: account.move recordset
        :param amount: float
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.register_payments_obj.with_context(ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        if journal:
            register_payments.write({"journal_id": journal.id})
        if amount:
            register_payments.write({"amount": amount})
        register_payments.action_create_payments()

    def _create_invoice(self, partner=False, inv_type="out_invoice", validate=False):
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
            "invoice_date": fields.Date.today(),
            "move_type": inv_type,
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
            invoice._post()
        return invoice

    def _get_selection_label(self, invoice, field):
        """
        Get the translated label of the invoice selection field
        :param invoice: account.move recordset
        :param field: str
        :return: str
        """
        technical_type = invoice[field]
        type_dict = dict(invoice._fields.get(field)._description_selection(invoice.env))
        return type_dict.get(technical_type, technical_type)
