# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.osv import expression

from odoo.addons.component.core import Component


class InvoiceService(Component):
    """Shopinvader service to expose invoices.
    """

    _inherit = [
        "shopinvader.abstract.mail.service",
        "abstract.shopinvader.download",
    ]
    _name = "shopinvader.invoice.service"
    _usage = "invoice"
    _expose_model = "account.move"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def to_openapi(self):
        res = super(InvoiceService, self).to_openapi()
        # Manually add route for HTTP GET download
        response = self._get_openapi_default_responses()
        response["200"] = {"description": "The file to download"}
        parameters = self._get_openapi_default_parameters()
        parameters.append(
            {
                "schema": {"type": "integer"},
                "description": "Item id",
                "required": True,
                "name": "id",
                "in": "path",
            }
        )
        res["paths"]["/{id}/download"] = {
            "get": {
                "responses": response,
                "parameters": parameters,
                "summary": "Get the invoice file",
            }
        }
        return res

    # Private implementation

    def _get_allowed_invoice_states(self):
        """Get invoice states.

        :return: list of str
        """
        return ["posted"]

    def _get_allowed_payment_states(self):
        """Get invoice payment states.

        :return: list of str
        """
        states = ["paid"]
        if self.shopinvader_backend.invoice_access_open:
            states += ["not_paid", "in_payment"]
        return states

    def _get_base_search_domain(self):
        """Domain used to retrieve requested invoices.

        This domain MUST TAKE CARE of restricting the access to the invoices
        visible for the current customer
        :return: Odoo domain
        """
        # The partner must be set and not be the anonymous one
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        invoices = self._get_available_invoices()
        domain_invoice_ids = [("id", "in", invoices.ids)]
        return expression.normalize_domain(
            expression.AND([domain_invoice_ids, self._get_domain_state()])
        )

    def _get_domain_state(self):
        domain_state = [("state", "in", self._get_allowed_invoice_states())]
        domain_payment_state = [
            ("invoice_payment_state", "in", self._get_allowed_payment_states())
        ]
        return expression.AND([domain_state, domain_payment_state])

    def _get_available_invoices(self):
        """Retrieve invoices for current customer."""
        # here we only allow access to invoices linked to a sale order of the
        # current customer
        if self.shopinvader_backend.invoice_linked_to_sale_only:
            so_domain = self._get_sale_order_domain()
            # invoice_ids on sale.order is a computed field...
            # to avoid to duplicate the logic, we search for the sale orders
            # and check if the invoice_id is into the list of sale.invoice_ids
            sales = self.env["sale.order"].search(so_domain)
            invoices = sales.mapped("invoice_ids")
        else:
            invoices = self.env["account.move"].search(
                [
                    ("partner_id", "=", self.partner.id),
                    ("type", "in", ["out_invoice", "out_refund"]),
                ]
            )
        return invoices

    def _get_sale_order_domain(self):
        sale_service = self.component(usage="sales")
        return sale_service._get_base_search_domain()

    def _get_report_action(self, target, params=None):
        """Get the action/dict to generate the report.

        :param target: recordset
        :return: dict/action
        """
        report = self.shopinvader_backend.invoice_report_id
        if not report:
            report = self.env.ref("account.account_invoices")
        return report.report_action(target, config=False)
