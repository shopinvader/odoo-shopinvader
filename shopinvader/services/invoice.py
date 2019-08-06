# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mimetypes

from odoo import _
from odoo.addons.base_rest.components.service import (
    skip_secure_response,
    to_int,
)
from odoo.addons.component.core import Component
from odoo.exceptions import MissingError
from odoo.http import content_disposition, request
from odoo.osv import expression


class InvoiceService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.invoice.service"
    _usage = "invoice"
    _expose_model = "account.invoice"
    _description = "Service providing a method to download invoices"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @skip_secure_response
    def download(self, _id, **params):
        """
        Get invoice file. This method is also callable by HTTP GET
        """
        invoice = self._get(_id)
        headers, content = self._get_binary_content(invoice)
        if not content:
            raise MissingError(_("No content found for invoice %s") % _id)
        response = request.make_response(content, headers)
        response.status_code = 200
        return response

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

    # Validator

    def _validator_download(self):
        return {"id": {"type": "integer", "required": True, "coerce": to_int}}

    # Private implementation

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
        return expression.normalize_domain(
            [("id", "in", invoice_ids), ("state", "=", "paid")]
        )

    def _get_binary_content(self, invoice):
        """
        Generate the invoice report....
        :param invoice:
          :returns: (headers, content)
        """
        # ensure the report is generated
        invoice_report_def = invoice.invoice_print()
        report_name = invoice_report_def["report_name"]
        report_type = invoice_report_def["report_type"]
        content, format = self.env["ir.actions.report.xml"].render_report(
            res_ids=invoice.ids,
            name=report_name,
            data={"report_type": report_type},
        )
        report = self._get_report(report_name, report_type)
        filename = self._get_binary_content_filename(invoice, report, format)
        mimetype = mimetypes.guess_type(filename)
        if mimetype:
            mimetype = mimetype[0]
        headers = [
            ("Content-Type", mimetype),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Disposition", content_disposition(filename)),
            ("Content-Length", len(content)),
        ]
        return headers, content

    def _get_report(self, report_name, report_type):
        domain = [
            ("report_type", "=", report_type),
            ("report_name", "=", report_name),
        ]
        return self.env["ir.actions.report.xml"].search(domain)

    def _get_binary_content_filename(self, invoice, report, format):
        return "{}.{}".format(report.name, format)
