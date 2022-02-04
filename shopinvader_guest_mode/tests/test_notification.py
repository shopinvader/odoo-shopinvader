# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import CommonCase, NotificationCaseMixin


class NotificationCustomerCase(CommonCase, NotificationCaseMixin):
    def setUp(self):
        super().setUp()
        self.data = {
            "email": "my_guest@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": self.env.ref("base.fr").id},
        }
        self.backend.write(
            {
                "is_guest_mode_allowed": True,
            }
        )
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="guest")

    def test_new_customer_welcome_disabled(self):
        """
        Ensure the notification new_customer_welcome is disabled for guest
        """
        self.assertTrue(
            self.backend.notification_ids.filtered(
                lambda n: n.notification_type == "new_customer_welcome"
            )
        )
        res = self.service.dispatch("create", params=self.data).get("data")
        partner = self.env["res.partner"].browse(res.get("id"))
        job = self._find_notification_job(
            name="Notify new_customer_welcome for res.partner,%d" % partner.id
        )
        self.assertFalse(job)
