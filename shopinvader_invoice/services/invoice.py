# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class InvoiceService(Component):
    _inherit = "shopinvader.invoice.service"

    def get(self, _id):
        """
        Get info about given invoice id.
        :param _id: int
        :return: dict/json
        """
        invoice = self._get(_id)
        result = {"data": self._to_json(invoice)[0]}
        return result

    def search(self, **params):
        """
        Get every invoices related to logged user
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def _validator_get(self):
        return {}

    def _validator_search(self):
        """
        Validator for the search
        :return: dict
        """
        default_validator = self._default_validator_search()
        default_validator.pop("scope", {})
        default_validator.pop("domain", {})
        return default_validator

    def _validator_return_get(self):
        """
        Output validator for the search
        :return: dict
        """
        invoice_schema = self._get_return_invoice_schema()
        schema = {"data": {"type": "dict", "schema": invoice_schema}}
        return schema

    def _validator_return_search(self):
        """
        Output validator for the search
        :return: dict
        """
        invoice_schema = self._get_return_invoice_schema()
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": invoice_schema},
            },
        }
        return schema

    def _get_return_invoice_schema(self):
        """
        Get details about invoice to return
        (used into validator_return)
        :return: dict
        """
        invoice_schema = {
            "invoice_id": {"type": "integer"},
            "number": {"type": "string"},
            "date_invoice": {"type": "string"},
            "amount_total": {"type": "float"},
            "amount_total_signed": {"type": "float"},
            "amount_tax": {"type": "float"},
            "amount_untaxed": {"type": "float"},
            "amount_untaxed_signed": {"type": "float"},
            "amount_due": {"type": "float"},
            "type": {"type": "string"},
            "state": {"type": "string"},
            "type_label": {"type": "string"},
            "state_label": {"type": "string"},
        }
        return invoice_schema

    def _get_parser_invoice(self):
        """
        Get the parser of account.invoice
        :return: list
        """
        to_parse = [
            "id:invoice_id",
            "number",
            "date_invoice",
            "amount_total",
            "amount_total_signed",
            "amount_tax",
            "amount_untaxed",
            "amount_untaxed_signed",
            "state",
            "type",
            "residual:amount_due",
        ]
        return to_parse

    def _to_json_invoice(self, invoice):
        invoice.ensure_one()
        parser = self._get_parser_invoice()
        values = invoice.jsonify(parser)[0]
        values.update(
            {
                "type_label": self._get_selection_label(invoice, "type"),
                "state_label": self._get_selection_label(invoice, "state"),
            }
        )
        return values

    def _to_json(self, invoices):
        res = []
        for invoice in invoices:
            res.append(self._to_json_invoice(invoice))
        return res
