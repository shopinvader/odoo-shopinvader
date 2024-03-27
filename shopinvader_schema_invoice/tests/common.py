# Copyright 2023 ACSONE SA/NV (https://acsone.eu).
# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin


class InvoiceCaseMixin:
    @classmethod
    def _setup_invoice_data(cls):
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@test.eu",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 10.0,
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "testbank1"}
        )
        cls.account_receivable = cls.env["account.account"].create(
            {
                "name": "test receive",
                "code": "testreceive",
                "account_type": "asset_receivable",
                "company_id": cls.env.company.id,
                "reconcile": True,
            }
        )
        cls.bank_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "bank1"}
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "sale", "code": "sale1"}
        )


class SchemaInvoiceCase(TransactionCase, ExtendableMixin, InvoiceCaseMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls._setup_invoice_data()


# ripped out of shopinvader_invoice and refactored into reusable methods
# TODO: split to its own helper module?


def create_invoice(
    env, partner, product, inv_type="out_invoice", validate=False, account=None, **vals
):
    """
    Create a new invoice

    :param partner: res.partner
    :param inv_type: str
    :param validate: bool
    :return: account.move record
    """
    account = account or product.categ_id.property_account_expense_categ_id
    values = {
        "partner_id": partner.id,
        "partner_shipping_id": partner.id,
        "invoice_date": fields.Date.today(),
        "move_type": inv_type,
        "invoice_line_ids": [
            (
                0,
                False,
                {
                    "product_id": product.id,
                    "quantity": 10,
                    "price_unit": 1250,
                    "account_id": account.id,
                    "name": product.display_name,
                },
            )
        ],
    }
    values.update(vals)
    invoice = env["account.move"].create(values)
    if validate:
        invoice._post()
    return invoice


def add_payment(invoice, journal=False, amount=False):
    """
    Make payment for given invoice

    :param invoice: account.move recordset
    :param amount: float
    :return: bool
    """
    payment_wiz_model = invoice.env["account.payment.register"]
    ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
    wizard_obj = payment_wiz_model.with_context(**ctx)
    register_payments = wizard_obj.create(
        {
            "payment_date": fields.Date.today(),
            "journal_id": journal.id,
        }
    )
    if amount:
        register_payments.write({"amount": amount})
    register_payments.action_create_payments()


def get_selection_label(self, rec, field):
    """
    Get the translated label of the record selection field
    """
    type_dict = dict(rec._fields.get(field)._description_selection(rec.env))
    return type_dict.get(rec[field], rec[field])
