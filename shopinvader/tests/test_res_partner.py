# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.exceptions import ValidationError

from odoo.addons.component.tests.common import SavepointComponentCase


class TestResPartner(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.unique_email = datetime.now().isoformat() + "@test.com"

    def test_unique_email_partner(self):
        self.assertFalse(self.env["res.partner"]._is_partner_duplicate_prevented())
        partner_1 = self.env["res.partner"].create(
            {"email": self.unique_email, "name": "test partner"}
        )
        # by default we can create partner with same email
        partner_2 = self.env["res.partner"].create(
            {"email": self.unique_email, "name": "test partner 2"}
        )
        self.env["ir.config_parameter"].create(
            {"key": "shopinvader.no_partner_duplicate", "value": "True"}
        )
        self.assertTrue(self.env["res.partner"]._is_partner_duplicate_prevented())
        # once you've changed the config to dispable duplicate partner
        # it's no more possible to create a partner with the same email
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["res.partner"].create(
                {"email": self.unique_email, "name": "test partner 3"}
            )

        # unicity constrains is only applicable on active records
        partners = partner_1 | partner_2
        partners.write({"active": False})
        self.env["res.partner"].create(
            {"email": self.unique_email, "name": "test partner 3"}
        )
