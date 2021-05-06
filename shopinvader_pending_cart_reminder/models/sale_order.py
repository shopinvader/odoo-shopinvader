# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pending_cart_reminder_sent_dt = fields.Datetime(
        help="Pending cart reminder sent date/hour", default=False
    )

    @api.model
    def _get_sale_order_domain_for_reminder(self, backend, reminder_date):
        """
        Get the domain to have sale orders concerned by the reminder
        :param backend: shopinvader.backend recordset
        :param reminder_date: str
        :return: list of tuple (domain)
        """
        anonymous_partner = backend.anonymous_partner_id
        domain = [
            ("partner_id", "!=", anonymous_partner.id),
            ("shopinvader_backend_id", "=", backend.id),
            ("typology", "=", "cart"),
            ("pending_cart_reminder_sent_dt", "=", False),
            ("write_date", "<=", reminder_date),
            ("create_date", ">=", backend.reminder_start_date),
        ]
        return domain

    @api.model
    def _get_pending_cart_to_remind(self, backend, last_write_dt):
        """
        Get sale orders for the reminder
        :param backend: shopinvader.backend recordset
        :param last_write_dt: str
        :return: sale.order recordset
        """
        domain = self._get_sale_order_domain_for_reminder(backend, last_write_dt)
        return self.search(domain)

    def _execute_pending_cart_reminder(self):
        """
        Send the email and update the sale order (to avoid multi reminder)
        :return: bool
        """
        for sale_order in self:
            backend = sale_order.shopinvader_backend_id
            if backend.pending_cart_reminder_template_id:
                backend.pending_cart_reminder_template_id.send_mail(sale_order.id)
        # Even if the pending_cart_reminder_template_id is not filled we have
        # to fill this pending_cart_reminder_sent_dt. Otherwise, when the
        # pending_cart_reminder_template_id will be filled, old SO could
        # launch an email.
        self.write({"pending_cart_reminder_sent_dt": fields.Datetime.now()})

    @api.model
    def _get_pending_cart_last_write_dt(self, backend):
        """
        Get the reminder date
        :param backend: shopinvader.backend
        :return: datetime
        """
        reminder_date_dt = fields.Datetime.from_string(fields.Datetime.now())
        reminder_date_dt -= timedelta(hours=backend.pending_cart_reminder_delay)
        return reminder_date_dt

    @api.model
    def launch_pending_cart_reminder(self):
        """
        Launch the reminder
        :return:
        """
        backend_domain = [
            ("pending_cart_reminder_delay", ">", 0),
            ("pending_cart_reminder_template_id", "!=", False),
        ]
        backends = self.env["shopinvader.backend"].search(backend_domain)
        for backend in backends:
            reminder_date = self._get_pending_cart_last_write_dt(backend)
            reminder_date_txt = fields.Datetime.to_string(reminder_date)
            sale_orders = self._get_pending_cart_to_remind(backend, reminder_date_txt)
            if sale_orders:
                sale_orders._execute_pending_cart_reminder()
