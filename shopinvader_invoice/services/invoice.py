# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import (
    odoo_env,
    paging,
    authenticated_partner
)
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from ..schemas.invoice import AccountMove

from ..models.fast_api_endpoint import invoice_api_router


@invoice_api_router.get(
    "/invoices",
    response_model=PagedCollection[AccountMove]
    dependencies=[Depends(authenticated_partner)],
)
async def search(
    env: Environment = Depends(odoo_env),  # noqa: B008
    paging: Paging = Depends(paging),
    partner: ResPartner = Depends(authenticated_partner),
) -> PagedCollection[AccountMove]:  # noqa: B008
    """Get the list of partner invoices
    """
    domain = [("partner_id", "=", partner.id)]
    count = env["account.move"].search_count(domain)
    orders = env["account.move"].search(domain, limit=paging.limit, offset=paging.offset)
    return PagedCollection[AccountMove](
        total=count,
        items=[AccountMove.from_orm(order) for invoice in invoices],
        )

#from odoo.addons.component.core import Component
#
#
#class InvoiceService(Component):
#    _inherit = "shopinvader.invoice.service"
#
#    def get(self, _id):
#        """
#        Get info about given invoice id.
#        :param _id: int
#        :return: dict/json
#        """
#        invoice = self._get(_id)
#        result = {"data": self._to_json(invoice)[0]}
#        return result
#
#    def search(self, **params):
#        """
#        Get every invoices related to logged user
#        :param params: dict/json
#        :return: dict
#        """
#        return self._paginate_search(**params)
#
#    def _validator_get(self):
#        return {}
#
#    def _validator_search(self):
#        """
#        Validator for the search
#        :return: dict
#        """
#        default_validator = self._default_validator_search()
#        default_validator.pop("scope", {})
#        default_validator.pop("domain", {})
#        return default_validator
#
#    def _validator_return_get(self):
#        """
#        Output validator for the search
#        :return: dict
#        """
#        invoice_schema = self._get_return_invoice_schema()
#        schema = {"data": {"type": "dict", "schema": invoice_schema}}
#        return schema
#
#    def _validator_return_search(self):
#        """
#        Output validator for the search
#        :return: dict
#        """
#        invoice_schema = self._get_return_invoice_schema()
#        schema = {
#            "size": {"type": "integer"},
#            "data": {
#                "type": "list",
#                "schema": {"type": "dict", "schema": invoice_schema},
#            },
#        }
#        return schema
#
#    def _get_return_invoice_schema(self):
#        """
#        Get details about invoice to return
#        (used into validator_return)
#        :return: dict
#        """
#        invoice_schema = {
#            "invoice_id": {"type": "integer"},
#            "number": {"type": "string"},
#            "payment_reference": {
#                "type": "string",
#                "required": False,
#                "nullable": True,
#            },
#            "date_invoice": {"type": "string"},
#            "date_due": {
#                "type": "string",
#                "required": False,
#                "nullable": True,
#            },
#            "amount_total": {"type": "float"},
#            "amount_total_signed": {"type": "float"},
#            "amount_tax": {"type": "float"},
#            "amount_untaxed": {"type": "float"},
#            "amount_untaxed_signed": {"type": "float"},
#            "amount_due": {"type": "float"},
#            "type": {"type": "string"},
#            "state": {"type": "string", "allowed": ["draft", "open", "cancel"]},
#            "payment_state": {
#                "type": "string",
#                "allowed": [
#                    "not_paid",
#                    "paid",
#                    "partial",
#                    "reversed",
#                    "invoicing_legacy",
#                ],
#            },
#            "type_label": {"type": "string"},
#            "state_label": {"type": "string"},
#            "payment_state_label": {"type": "string"},
#        }
#        return invoice_schema
#
#    def _get_shopinvader_state(self, record, field):
#        """Allows to not redefine service exposed values.
#        "posted" state => "open"
#        """
#        return "open" if record.state == "posted" else record.state
#
#    def _get_parser_invoice(self):
#        """
#        Get the parser of account.move
#        :return: list
#        """
#        to_parse = [
#            "id:invoice_id",
#            "name:number",
#            "payment_reference",
#            "invoice_date:date_invoice",
#            "invoice_date_due:date_due",
#            "amount_total",
#            "amount_total_signed",
#            "amount_tax",
#            "amount_untaxed",
#            "amount_untaxed_signed",
#            ("state", self._get_shopinvader_state),
#            "payment_state",
#            "move_type:type",
#            "amount_residual:amount_due",
#        ]
#        return to_parse
#
#    def _to_json_invoice(self, invoice):
#        invoice.ensure_one()
#        parser = self._get_parser_invoice()
#        values = invoice.jsonify(parser, one=True)
#        values.update(
#            {
#                "type_label": self._get_selection_label(invoice, "move_type"),
#                "state_label": self._get_selection_label(invoice, "state"),
#                "payment_state_label": self._get_selection_label(
#                    invoice, "payment_state"
#                ),
#            }
#        )
#        return values
#
#    def _to_json(self, invoices, **kw):
#        res = []
#        for invoice in invoices:
#            res.append(self._to_json_invoice(invoice))
#        return res
