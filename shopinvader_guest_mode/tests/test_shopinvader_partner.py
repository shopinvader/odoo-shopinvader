# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from odoo.addons.component.tests.common import SavepointComponentCase


class TestShopinvaderPartner(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.is_guest_mode_allowed = True
        cls.shopinvader_partner = cls.env["shopinvader.partner"].create(
            {
                "email": "test@test.com",
                "name": "test partner",
                "is_guest": True,
                "backend_id": cls.backend.id,
            }
        )

    @mute_logger("odoo.sql_db")
    def test_unique_active(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            # try to create a second active partner with same email..
            self.env["shopinvader.partner"].create(
                {
                    "email": "test@test.com",
                    "name": "test partner",
                    "is_guest": True,
                    "backend_id": self.backend.id,
                }
            )
        # creeate 2 others inactives partner with the same email
        # (should not raise exception)
        self.env["shopinvader.partner"].create(
            {
                "email": "test@test.com",
                "name": "test partner",
                "is_guest": True,
                "backend_id": self.backend.id,
                "active": False,
            }
        )
        shopinvader_partner = self.env["shopinvader.partner"].create(
            {
                "email": "test@test.com",
                "name": "test partner",
                "is_guest": True,
                "backend_id": self.backend.id,
                "active": False,
            }
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            shopinvader_partner.active = True
            shopinvader_partner.flush()

    def test_expiry_dt(self):
        self.assertTrue(self.shopinvader_partner.expiry_dt)
        # expiry_dt is reset if is_guest is set to False
        self.shopinvader_partner.is_guest = False
        self.assertFalse(self.shopinvader_partner.expiry_dt)
        # expiry_dt is sent when is_guest is True
        self.shopinvader_partner.is_guest = True
        self.assertTrue(self.shopinvader_partner.expiry_dt)
        # the delay is now + number of days specified on the backend
        create_date = self.shopinvader_partner.create_date
        create_date = fields.Datetime.from_string(create_date)
        delay = self.backend.guest_account_expiry_delay
        expiry_dt = create_date + timedelta(days=delay)
        self.assertEqual(self.shopinvader_partner.expiry_dt, expiry_dt)
        # if we change the delay on the backend expiry_dt is recomputed
        delay = delay + 20
        self.backend.guest_account_expiry_delay = delay
        expiry_dt = create_date + timedelta(days=delay)
        self.assertEqual(self.shopinvader_partner.expiry_dt, expiry_dt)

    def test_deactivate_expired(self):
        self.assertTrue(self.shopinvader_partner.active)
        # put a date time in the past into database....
        self.env.cr.execute(
            """
            update shopinvader_partner
            set expiry_dt = '2018-01-01 12:00:00'
            where id = %s
        """,
            (self.shopinvader_partner.id,),
        )
        self.env["shopinvader.partner"]._deactivate_expired()
        self.assertFalse(self.shopinvader_partner.active)

    def test_guest_constrains(self):
        self.shopinvader_partner.search([(1, "=", 1)]).write({"is_guest": False})
        self.backend.is_guest_mode_allowed = False
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["shopinvader.partner"].create(
                {
                    "email": "email@email.com",
                    "name": "other partner",
                    "is_guest": True,
                    "backend_id": self.backend.id,
                }
            )
        self.backend.is_guest_mode_allowed = True
        binding = self.env["shopinvader.partner"].create(
            {
                "email": "email@email.com",
                "name": "other partner",
                "is_guest": True,
                "backend_id": self.backend.id,
            }
        )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.backend.is_guest_mode_allowed = False
        binding.is_guest = False
        self.backend.is_guest_mode_allowed = False
