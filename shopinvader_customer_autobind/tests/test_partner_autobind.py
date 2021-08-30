# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.bus.models.bus import json_dump
from odoo.addons.shopinvader.tests.common import CommonCase


class TestPartnerAutoBind(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.bind_new_customers = True
        cls.partner_obj = cls.env["res.partner"]
        cls.backend.new_customer_autobind_mail_template_id = cls.env.ref(
            "shopinvader_customer_autobind.mail_template_autobind_new_customers"
        )
        cls.mail_domain = [("body", "like", "%shop account has been created%")]

    def test_partner_autobind(self):
        # Create a partner without mail address
        # Check that one backend notification is done
        # Then, fill in the email
        # Check that links to concerned backend are done
        # Create a second partner with email
        # Check that links to concerned backend are done
        bus_bus = self.env["bus.bus"]
        domain = [
            (
                "channel",
                "=",
                json_dump(self.env.user.notify_warning_channel_name),
            )
        ]
        existing = bus_bus.search(domain)
        vals = {"name": "Test Autobind partner", "customer_rank": 1}
        self.partner_auto = self.partner_obj.create(vals)
        self.assertFalse(self.partner_auto.shopinvader_bind_ids)
        news = bus_bus.search(domain) - existing
        self.assertEqual(1, len(news))

        vals = {"email": "test1@test.com"}
        mail_before = self.env["mail.mail"].search(self.mail_domain)
        self.partner_auto.write(vals)
        mail_after = self.env["mail.mail"].search(self.mail_domain)
        self.assertEqual(1, len(mail_after - mail_before))
        self.assertEqual(1, len(self.partner_auto.shopinvader_bind_ids))

        vals = {
            "name": "Test Autobind partner 2",
            "customer_rank": 1,
            "email": "test@test.com",
        }
        existing = bus_bus.search(domain)
        self.partner_auto = self.partner_obj.create(vals)
        self.assertEqual(1, len(self.partner_auto.shopinvader_bind_ids))
        news = bus_bus.search(domain) - existing
        self.assertEqual(0, len(news))
        vals = {
            "name": "Test Contact partner 2",
            "customer_rank": 1,
            "email": "test_contact@test.com",
            "parent_id": self.partner_auto.id,
        }
        self.contact = self.partner_obj.create(vals)
        self.assertEqual(0, len(self.contact.shopinvader_bind_ids))
