# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ..schemas import Invoice, InvoiceAmount
from .common import SchemaInvoiceCase, create_invoice


class TestInvoiceSchema(SchemaInvoiceCase):
    def test_invoice_amount(self):
        invoice_rec = create_invoice(self.env, self.partner, self.product)
        inv_amount = InvoiceAmount.from_record(invoice_rec)
        expected = {
            "amount_tax": invoice_rec.amount_tax,
            "amount_untaxed": invoice_rec.amount_untaxed,
            "amount_total": invoice_rec.amount_total,
            "amount_due": invoice_rec.amount_residual,
        }
        self.assertEqual(inv_amount.model_dump(), expected)

    def test_invoice(self):
        invoice_rec = create_invoice(self.env, self.partner, self.product)
        invoice = Invoice.from_record(invoice_rec)
        expected = {
            "id": invoice_rec.id,
            "name": invoice_rec.name,
            "state": invoice_rec.state,
            "date_invoice": invoice_rec.invoice_date,
            "date_due": invoice_rec.invoice_date_due or None,
            "amount": InvoiceAmount.from_record(invoice_rec).model_dump(),
            "payment_state": invoice_rec.payment_state,
            "ref": invoice_rec.ref or "",
            "payment_reference": invoice_rec.payment_reference or "",
        }
        data = invoice.model_dump()
        self.assertEqual(data, expected)
