# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.component.tests.common import SavepointComponentCase


class TestShopinvaderBackend(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.is_guest_mode_allowed = True

    def test_guest_mode_constrains(self):
        # check that it's not possible to disable the guest mode if a
        # guest binding already exists
        shopinvader_partner = self.env["shopinvader.partner"].create(
            {
                "email": "test@test.com",
                "name": "test partner",
                "is_guest": True,
                "backend_id": self.backend.id,
            }
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.backend.is_guest_mode_allowed = False
        shopinvader_partner.is_guest = False
        self.backend.is_guest_mode_allowed = False

    def test_guest_mode_delay_constrains(self):
        # check that it's not possible to unset or put an invalid delay if
        # the guest mode is set on the backend
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.backend.guest_account_expiry_delay = False
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.backend.guest_account_expiry_delay = 0
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.backend.guest_account_expiry_delay = -1
        self.backend.guest_account_expiry_delay = 10
        self.assertEqual(self.backend.guest_account_expiry_delay, 10)
