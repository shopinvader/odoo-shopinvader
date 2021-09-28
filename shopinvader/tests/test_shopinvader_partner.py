# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from odoo.addons.component.tests.common import SavepointComponentCase


class TestShopinvaderPartner(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderPartner, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.unique_email = datetime.now().isoformat() + "@test.com"

    @mute_logger("odoo.sql_db")
    def test_unique_binding(self):
        self.env["shopinvader.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner",
                "backend_id": self.backend.id,
            }
        )
        with self.assertRaises(IntegrityError):
            self.env["shopinvader.partner"].create(
                {
                    "email": self.unique_email,
                    "name": "test partner",
                    "backend_id": self.backend.id,
                }
            )

    @mute_logger("odoo.models.unlink")
    def test_partner_duplicate(self):
        """
        Test that the partner are duplicated if we create 2 binding with the
        email (after having removed the first binding)
        :return:
        """
        self.assertFalse(
            self.env["res.partner"]._is_partner_duplicate_prevented()
        )
        # we create a first binding
        binding = self.env["shopinvader.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner",
                "backend_id": self.backend.id,
            }
        )
        # a partner has been created for this binding
        res = self.env["res.partner"].search(
            [("email", "=", self.unique_email)]
        )
        self.assertEqual(binding.record_id, res)
        # if we remove the partner and create a new binding with the same email
        # a new partner will be created
        binding.unlink()
        self.env["shopinvader.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner 2",
                "backend_id": self.backend.id,
            }
        )
        res = self.env["res.partner"].search(
            [("email", "=", self.unique_email)]
        )
        self.assertEqual(len(res), 2)

    def test_partner_no_duplicate(self):
        """
        Test that if a partner already exists with the same email, the binding
        will not create a new partner
        """
        # IMPORTANT: never call `execute` on settings in tests
        # otherwise is going to reset the env and screw computed fields.
        # We could call `set_values` instead but it loads a lot of things
        # that we don't need. Plus, is not going to show you what you can do to
        # change the behavior via config param.
        self.env["ir.config_parameter"].create(
            {"key": "shopinvader.no_partner_duplicate", "value": "True"}
        )
        self.assertTrue(
            self.env["res.partner"]._is_partner_duplicate_prevented()
        )
        vals = {"email": self.unique_email, "name": "test partner"}
        # create a partner...
        partner = self.env["res.partner"].create(vals)
        # create a binding
        binding = self.env["shopinvader.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner",
                "backend_id": self.backend.id,
            }
        )
        # the binding must be linked to the partner
        self.assertEqual(partner, binding.record_id)
        # no child should exists since all the values are the same on the
        # partner
        self.assertFalse(partner.child_ids)

    def test_partner_no_duplicate_child(self):
        """
        In this test we check that if a partner already exists for the binding
        but with different values, the binding is linked to the partner and a
        new child partner or partner is created to keep the information
        provided when creating the binding
        """
        self.env["ir.config_parameter"].create(
            {"key": "shopinvader.no_partner_duplicate", "value": "True"}
        )
        self.assertTrue(
            self.env["res.partner"]._is_partner_duplicate_prevented()
        )
        vals = {"email": self.unique_email, "name": "test partner"}
        # create a partner...
        partner = self.env["res.partner"].create(vals)
        self.assertFalse(partner.child_ids)
        # create a binding with the same email but an other name
        binding = self.env["shopinvader.partner"].create(
            {
                "email": self.unique_email,
                "name": "test other partner",
                "street": "my street",
                "backend_id": self.backend.id,
            }
        )
        self.assertEqual(partner, binding.record_id)
        partner.refresh()
        self.assertTrue(partner.child_ids)
        self.assertEqual(1, len(partner.child_ids))
        child = partner.child_ids
        self.assertEqual(child.name, "test other partner")
        self.assertEqual(child.street, "my street")

        # only one partner should exists with this email
        res = self.env["res.partner"].search(
            [("email", "=", self.unique_email)]
        )
        self.assertEqual(len(res), 1)
