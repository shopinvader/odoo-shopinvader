# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reminder_sent_datetime = fields.Datetime(
        help="Date/hour of last  (automatic) reminder", default=False
    )

    @api.model
    def _get_sale_order_for_reminder(self, backend, reminder_date):
        """
        Get sale orders for the reminder
        :param backend: shopinvader.backend
        :param reminder_date: str
        :return: sale.order recordset
        """
        anonymous_partner = backend.anonymous_partner_id
        domain = [
            ("partner_id", "!=", anonymous_partner.id),
            ("shopinvader_backend_id", "=", backend.id),
            ("typology", "=", "cart"),
            ("reminder_sent_datetime", "=", False),
            ("write_date", "<=", reminder_date),
        ]
        return self.search(domain)

    @api.multi
    def _execute_reminder(self):
        """
        Sent the email and update the sale order (to avoid multi reminder)
        :return: bool
        """
        for sale_order in self:
            backend = sale_order.shopinvader_backend_id
            backend.quotation_reminder_mail_template_id.send_mail(
                sale_order.id
            )
        self.write({"reminder_sent_datetime": fields.Datetime.now()})

    @api.model
    def _get_reminder_date(self, backend):
        """
        Get the reminder date
        :param backend: shopinvader.backend
        :return: datetime
        """
        reminder_date_dt = fields.Datetime.from_string(fields.Datetime.now())
        reminder_date_dt -= timedelta(hours=backend.quotation_reminder)
        return reminder_date_dt

    @api.model
    def launch_reminder(self):
        """
        Launch the reminder
        :return:
        """
        backend_domain = [
            ("quotation_reminder", ">", 0),
            ("quotation_reminder_mail_template_id", "!=", False),
        ]
        backends = self.env["shopinvader.backend"].search(backend_domain)
        for backend in backends:
            reminder_date = self._get_reminder_date(backend)
            reminder_date_txt = fields.Datetime.to_string(reminder_date)
            sale_orders = self._get_sale_order_for_reminder(
                backend, reminder_date_txt
            )
            if sale_orders:
                sale_orders._execute_reminder()
