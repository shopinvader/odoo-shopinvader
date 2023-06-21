# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields
from odoo.exceptions import AccessError, UserError

from odoo.addons.shopinvader.tests.common import CommonCase


class TestImpersonate(CommonCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("shopinvader.shopinvader_partner_1")
        with self.work_on_services() as work:
            self.service = work.component(usage="customer")

    def test_valid_token(self):
        self.partner.impersonate()
        res = self.service.dispatch(
            "impersonate",
            params={
                "token": self.partner.impersonate_token,
                "email": self.partner.email,
            },
        )
        self.assertIn("store_cache", res)
        self.assertIn("customer", res["store_cache"])
        self.assertIn("force_authenticate_customer", res)
        self.assertEqual(res["force_authenticate_customer"], "osiris@shopinvader.com")
        self.assertIn("redirect_to", res)
        self.assertEqual(res["redirect_to"], "http://locomotive.localtest.me:3000")

    def test_invalid_token(self):
        self.partner.impersonate()
        with self.assertRaisesRegex(UserError, "Invalid impersonate token"):
            self.service.dispatch(
                "impersonate",
                params={
                    "token": "wrong-token",
                    "email": self.partner.email,
                },
            )

    def test_expired_token(self):
        self.partner.impersonate()
        self.partner.datetime_expire_impersonate_token = fields.Datetime.subtract(
            fields.Datetime.now(), seconds=1
        )
        with self.assertRaisesRegex(UserError, "Invalid impersonate token"):
            self.service.dispatch(
                "impersonate",
                params={
                    "token": self.partner.impersonate_token,
                    "email": self.partner.email,
                },
            )

    def test_access_right(self):
        user = self.env.ref("base.user_demo")
        with self.assertRaisesRegex(
            AccessError, "You are not allowed to impersonate customer"
        ):
            self.partner.with_user(user).impersonate()
