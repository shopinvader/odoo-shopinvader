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
        cls.backend1 = cls.env.ref("shopinvader.backend_1")
        cls.backend2 = cls.env.ref("shopinvader.backend_2")

    def test_unique_email_partner(self):
        self.assertFalse(
            self.env["res.partner"]._is_partner_duplicate_prevented()
        )
        partner_1 = self.env["res.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner",
                "shopinvader_bind_ids": [
                    (0, False, {"backend_id": self.backend1.id})
                ],
            }
        )
        # by default we can create partner with shopinvader user with same email
        # as long as they are related to different backends
        partner_2 = self.env["res.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner 2",
                "shopinvader_bind_ids": [
                    (0, False, {"backend_id": self.backend2.id})
                ],
            }
        )

        # unlink partner_2 to validate the constrain after, to avoid having
        # to create a new backend for the test
        partner_2.shopinvader_bind_ids.unlink()
        partner_2.unlink()

        # activate no partner duplicate parameter
        self.env["ir.config_parameter"].create(
            {"key": "shopinvader.no_partner_duplicate", "value": "True"}
        )
        self.assertTrue(
            self.env["res.partner"]._is_partner_duplicate_prevented()
        )

        # once you've changed the config to disable duplicate partner
        # it's no more possible to create a partner with shopinvader user
        # with the same email
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["res.partner"].create(
                {
                    "email": self.unique_email,
                    "name": "test partner 2",
                    "shopinvader_bind_ids": [
                        (0, False, {"backend_id": self.backend2.id})
                    ],
                }
            )

        # unicity constrains is only applicable on partners with
        # shopinvader user
        self.env["res.partner"].create(
            {"email": self.unique_email, "name": "test partner 2"}
        )

        # unicity constrains is also only applicable on active records
        partner_1.write({"active": False})
        self.env["res.partner"].create(
            {
                "email": self.unique_email,
                "name": "test partner 3",
                "shopinvader_bind_ids": [
                    (0, False, {"backend_id": self.backend2.id})
                ],
            }
        )
