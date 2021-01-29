# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class CommonNotificationCase(CommonCase):
    def setUp(self):
        super(CommonNotificationCase, self).setUp()
        self.cart = self.env.ref("shopinvader.sale_order_2")

    def _check_notification(self, notif_type, record):
        notif = self.env["shopinvader.notification"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("notification_type", "=", notif_type),
            ]
        )
        vals = notif.template_id.generate_email(record.id)
        message = self.env["mail.message"].search(
            [
                ("subject", "=", vals["subject"]),
                ("model", "=", record._name),
                ("res_id", "=", record.id),
            ]
        )
        self.assertEqual(len(message), 1)

    def _check_job_priority(self, job, notif_type=False, force_priority=False):
        """
        Ensure the job priority is correct
        :param job: queue.job recordset
        :param notif_type: str
        :param force_priority: int
        :return: bool
        """
        if isinstance(force_priority, bool):
            notification = self.env["shopinvader.notification"].search(
                [
                    ("backend_id", "=", self.backend.id),
                    ("notification_type", "=", notif_type),
                ],
                limit=1,
            )
            priority = notification.queue_job_priority
        else:
            priority = force_priority
        self.assertEquals(priority, job.priority)
        return True


class NotificationCartCase(CommonNotificationCase):
    def test_cart_notification(self):
        self._init_job_counter()
        self.cart.action_confirm_cart()
        self._check_nbr_job_created(1)
        self._check_job_priority(self.created_jobs, "cart_confirmation")
        self._perform_created_job()
        self._check_notification("cart_confirmation", self.cart)

    def test_sale_notification(self):
        priority = 30
        self.env["shopinvader.notification"].search([]).write(
            {"queue_job_priority": priority}
        )
        self.cart.action_confirm_cart()
        self._init_job_counter()
        self.cart.action_confirm()
        self._check_nbr_job_created(1)
        self._check_job_priority(
            self.created_jobs, "sale_confirmation", force_priority=priority
        )
        self._perform_created_job()
        self._check_notification("sale_confirmation", self.cart)

    def test_invoice_notification(self):
        self.cart.action_confirm_cart()
        self.cart.action_confirm()
        for line in self.cart.order_line:
            line.qty_delivered = line.product_uom_qty
        self.cart.action_invoice_create()
        self._init_job_counter()
        self.cart.invoice_ids.action_invoice_open()
        self._check_nbr_job_created(1)
        self._check_job_priority(self.created_jobs, "invoice_open")
        self._perform_created_job()
        self._check_notification("invoice_open", self.cart.invoice_ids[0])

    def test_new_customer_welcome(self):
        data = {
            "email": "new@customer.example.com",
            "external_id": "D5CdkqOEL",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "mobile": "0685485454",
            "country": {"id": self.env.ref("base.fr").id},
        }
        self._init_job_counter()
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            service = work.component(usage="customer")
            res = service.dispatch("create", params=data)["data"]
            partner = self.env["res.partner"].browse(res["id"])
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification("new_customer_welcome", partner)
