# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mimetypes

from odoo import _
from odoo.exceptions import MissingError
from odoo.http import content_disposition, request
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent


class AbstractDownload(AbstractComponent):
    """
    Class used to define behaviour to generate and download a document.
    You only have to inherit this AbstractComponent and implement the function
    _get_report_action(...).

    Example for invoice service:
    Class InvoiceService(Component):
        _inherit = [
            "base.shopinvader.service",
            "abstract.shopinvader.download",
        ]
        _name = "shopinvader.invoice.service"

        def _get_report_action(self, target, params):
            return target.invoice_print()
    """

    _name = "abstract.shopinvader.download"

    # This function should be overwritten
    def _get_report_action(self, target, params=None):
        """
        Get the action/dict to generate the report
        :param target: recordset
        :param params: dict
        :return: dict/action
        """
        raise NotImplementedError()

    @restapi.method(
        routes=[(["/<int:_id>/download"], "GET")],
        output_param=restapi.BinaryData(required=True),
    )
    def download(self, _id, **params):
        """
        Get target file. This method is also callable by HTTP GET
        """
        params = params or {}
        target = self._get(_id)
        headers, content = self._get_binary_content(target, params=params)
        if not content:
            raise MissingError(_("No content found for %s") % _id)
        response = request.make_response(content, headers)
        response.status_code = 200
        return response

    def _get_binary_content(self, target, params=None):
        """
        Generate the report for the given target
        :param target:
        :param params: dict
        :returns: (headers, content)
        """
        # Ensure the report is generated
        target_report_def = self._get_report_action(target, params=params)
        report_name = target_report_def.get("report_name")
        report_type = target_report_def.get("report_type")
        report = self._get_report(report_name, report_type)
        content, extension = report._render(
            target.ids, data={"report_type": report_type}
        )
        filename = self._get_binary_content_filename(
            target, report, extension, params=params
        )
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

    def _get_report(self, report_name, report_type, params=None):
        """
        Load the report recordset
        :param report_name: str
        :param report_type: str
        :param params: dict
        :return: ir.actions.report recordset
        """
        domain = [
            ("report_type", "=", report_type),
            ("report_name", "=", report_name),
        ]
        return self.env["ir.actions.report"].search(domain)

    def _get_binary_content_filename(self, target, report, extension, params=None):
        """
        Build the filename
        :param target: recordset
        :param report: ir.actions.report.xml recordset
        :param format: str
        :param params: dict
        :return: str
        """
        if report.print_report_name and not len(target) > 1:
            report_name = safe_eval(
                report.print_report_name, {"object": target, "time": time}
            )
            return "{}.{}".format(report_name, extension)
        return "{}.{}".format(report.name, extension)
