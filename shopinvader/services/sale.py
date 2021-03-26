# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero
from odoo.tools.translate import _

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class SaleService(Component):
    """Shopinvader service to expose sale orders records."""

    _inherit = [
        "shopinvader.abstract.sale.service",
        "abstract.shopinvader.download",
    ]
    _name = "shopinvader.sale.service"
    _usage = "sales"
    _expose_model = "sale.order"
    _description = __doc__

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
        return self.env.ref("sale.action_report_saleorder").report_action(
            target, config=False
        )

    def ask_email_invoice(self, _id):
        """
        Ask to receive invoices related to sale ID by email
        :param _id: int
        :return:
        """
        self._ask_email_invoice = True
        return self.ask_email(_id)

    def cancel(self, _id):
        order = self._get(_id)
        self._cancel(order)
        return self._to_json(order)[0]

    def reset_to_cart(self, _id):
        order = self._get(_id)
        self._cancel(order, reset_to_cart=True)
        res = self._to_json(order)[0]
        return {
            "data": res,
            "set_session": {"cart_id": res["id"]},
            "store_cache": {"cart": res},
        }

    # Validator
    def _validator_search(self):
        default_search_validator = self._default_validator_search()
        default_search_validator.pop("domain", {})
        default_search_validator.update({"id": {"coerce": to_int, "type": "integer"}})
        return default_search_validator

    def _validator_ask_email_invoice(self):
        return self._validator_ask_email()

    def _validator_cancel(self):
        return {}

    def _validator_reset_to_cart(self):
        return {}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get_base_search_domain(self):
        return expression.normalize_domain(
            self._default_domain_for_partner_records() + [("typology", "=", "sale")]
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
        return super(SaleService, self)._launch_notification(target, notif_type)

    def _convert_one_sale(self, sale):
        res = super(SaleService, self)._convert_one_sale(sale)
        res["invoices"] = self._convert_invoices(self._get_invoices(sale))
        return res

    def _get_invoices(self, sale):
        invoices = sale.sudo().invoice_ids
        invoice_service = self.component(usage="invoice")
        domain_state = invoice_service._get_domain_state()
        return invoices.filtered_domain(domain_state)

    def _is_cancel_allowed(self, sale):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in sale.order_line:
            if not float_is_zero(
                line.qty_delivered, precision_digits=precision
            ) or not float_is_zero(line.qty_invoiced, precision_digits=precision):
                raise UserError(
                    _("Orders that have been delivered or invoiced cannot be edited.")
                )
        return True

    def _cancel(self, sale, reset_to_cart=False):
        if not self._is_cancel_allowed(sale):
            raise UserError(_("This order cannot be cancelled"))
        sale.action_cancel()
        if reset_to_cart:
            sale.action_draft()
            sale.typology = "cart"
        return sale

    def _convert_invoices(self, invoices):
        return [self._convert_one_invoice(invoice) for invoice in invoices]

    def _convert_one_invoice(self, invoice):
        return {
            "id": invoice.id,
            "name": invoice.name,
            "date": invoice.invoice_date or None,
        }
