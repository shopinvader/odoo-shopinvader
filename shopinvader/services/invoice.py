# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.component.core import Component
from odoo.osv import expression


class InvoiceService(Component):
    _inherit = ["base.shopinvader.service", "abstract.shopinvader.download"]
    _name = "shopinvader.invoice.service"
    _usage = "invoices"
    _expose_model = "account.invoice"
    _description = "Service providing a method to download invoices"

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
        """
        Get every invoice states allowed to return on the service.
        :return: list of str
        """
        return ["paid"]

    def _get_base_search_domain(self):
        """
        This method must provide a domain used to retrieve the requested
        invoice.

        This domain MUST TAKE CARE of restricting the access to the invoices
        visible for the current customer
        :return: Odoo domain
        """
        # The partner must be set and not be the anonymous one
        if not self._is_logged():
            return expression.FALSE_DOMAIN

        # here we only allow access to invoices linked to a sale order of the
        # current customer
        so_domain = [
            ("partner_id", "=", self.partner.id),
            ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
            ("typology", "=", "sale"),
        ]
        # invoice_ids on sale.order is a computed field...
        # to avoid to duplicate the logic, we search for the sale orders
        # and check if the invoice_id is into the list of sale.invoice_ids
        sales = self.env["sale.order"].search(so_domain)
        invoice_ids = sales.mapped("invoice_ids").ids
        states = self._get_allowed_invoice_states()
        return expression.normalize_domain(
            [("id", "in", invoice_ids), ("state", "in", states)]
        )

    def _get_report_action(self, target, params=None):
        """
        Get the action/dict to generate the report
        :param target: recordset
        :return: dict/action
        """
        return target.invoice_print()


class DeprecatedInvoiceService(Component):
    _inherit = "shopinvader.invoice.service"
    _name = "shopinvader.deprecated.invoice.service"
    _usage = "invoice"
    _description = "Deprecated Service use 'invoices' instead"
