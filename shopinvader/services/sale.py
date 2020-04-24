# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv import expression


class SaleService(Component):
    _inherit = [
        "shopinvader.abstract.sale.service",
        "abstract.shopinvader.download",
    ]
    _name = "shopinvader.sale.service"
    _usage = "sales"
    _expose_model = "sale.order"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        order = self._get(_id)
        return self._to_json(order)[0]

    def search(self, **params):
        return self._paginate_search(**params)

    def _get_report_action(self, target, params=None):
        """
        Get the action/dict to generate the report
        :param target: recordset
        :param params: dict
        :return: dict/action
        """
        return target.print_quotation()

    def ask_email_invoice(self, _id):
        """
        Ask to receive invoices related to sale ID by email
        :param _id: int
        :return:
        """
        self._ask_email_invoice = True
        return self.ask_email(_id)

    # Validator
    def _validator_search(self):
        default_search_validator = self._default_validator_search()
        default_search_validator.pop("domain", {})
        default_search_validator.update(
            {"id": {"coerce": to_int, "type": "integer"}}
        )
        return default_search_validator

    def _validator_ask_email_invoice(self):
        return self._validator_ask_email()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get_base_search_domain(self):
        return expression.normalize_domain(
            [
                ("partner_id", "child_of", self.partner.id),
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
                ("typology", "=", "sale"),
            ]
        )

    def _get_email_notification_type(self, record):
        """
        Inherit to add the notification type for invoices related to this SO
        :param record: target record
        :return: str
        """
        result = super(SaleService, self)._get_email_notification_type(record)
        if getattr(self, "_ask_email_invoice", False):
            result = "invoice_send_email"
        return result

    def _launch_notification(self, target, notif_type):
        """
        Action to launch the notification (on the current backend) for the
        given record
        :param target: record
        :param notif_type: str
        :return: bool
        """
        if notif_type == "invoice_send_email":
            target = target.invoice_ids
        return super(SaleService, self)._launch_notification(
            target, notif_type
        )

    def _convert_one_sale(self, sale):
        res = super(SaleService, self)._convert_one_sale(sale)
        res["invoices"] = self._convert_invoices(sale.sudo())
        return res

    def _convert_invoices(self, sale):
        res = []
        for invoice in sale.invoice_ids.filtered(lambda i: i.state == "paid"):
            res.append(self._convert_one_invoice(invoice))
        return res

    def _convert_one_invoice(self, invoice):
        return {
            "id": invoice.id,
            "name": invoice.number,
            "date": invoice.date_invoice or None,
        }
