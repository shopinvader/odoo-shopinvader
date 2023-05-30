# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.addons.shopinvader import utils  # pylint: disable=W7950

from .common import CommonCase


class TestUtils(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invader_partner = cls.env.ref("shopinvader.shopinvader_partner_1")

    def test_partner_work_ctx(self):
        ctx = utils.get_partner_work_context(self.invader_partner)
        expected = {
            "partner": self.invader_partner.record_id,
            "partner_user": self.invader_partner.record_id,
            "invader_partner": self.invader_partner,
            "invader_partner_user": self.invader_partner,
        }
        self.assertEqual(ctx, expected)

    def test_partner_work_ctx_custom(self):
        new_invader_partner = self._create_invader_partner(
            self.env,
            name="Just A User",
            email="just@auser.com",
            parent_id=self.invader_partner.record_id.id,
        )
        # Simulate `get_shop_partner` give us another partner eg: the parent
        with mock.patch.object(
            type(new_invader_partner.record_id), "get_shop_partner"
        ) as mocked:
            mocked.return_value = new_invader_partner.record_id.parent_id
            ctx = utils.get_partner_work_context(new_invader_partner)
        expected = {
            "partner": self.invader_partner.record_id,
            "partner_user": new_invader_partner.record_id,
            "invader_partner": self.invader_partner,
            "invader_partner_user": new_invader_partner,
        }
        self.assertEqual(ctx, expected)

    def test_load_partner_work_ctx(self):
        with utils.work_on_service(self.env, shopinvader_backend=self.backend) as work:
            service = work.component(usage="customer")
            service._load_partner_work_context(self.invader_partner)
        expected = {
            "partner": self.invader_partner.record_id,
            "partner_user": self.invader_partner.record_id,
            "invader_partner": self.invader_partner,
            "invader_partner_user": self.invader_partner,
        }
        for k, v in expected.items():
            self.assertEqual(getattr(service, k), v)

    def test_reset_partner_work_ctx(self):
        with utils.work_on_service(self.env, shopinvader_backend=self.backend) as work:
            service = work.component(usage="customer")
            service._load_partner_work_context(self.invader_partner)
        service.work.whatever_shall_be_kept = "something"
        service._reset_partner_work_context()
        expected = {
            "partner": self.env["res.partner"].browse(),
            "partner_user": self.env["res.partner"].browse(),
            "invader_partner": self.env["shopinvader.partner"].browse(),
            "invader_partner_user": self.env["shopinvader.partner"].browse(),
        }
        for k, v in expected.items():
            self.assertEqual(getattr(service, k), v)

    def test_work_on_service_with_partner(self):
        with utils.work_on_service_with_partner(self.env, self.invader_partner) as work:
            service = work.component(usage="customer")
            service._load_partner_work_context(self.invader_partner)
        expected = {
            "partner": self.invader_partner.record_id,
            "partner_user": self.invader_partner.record_id,
            "invader_partner": self.invader_partner,
            "invader_partner_user": self.invader_partner,
        }
        for k, v in expected.items():
            self.assertEqual(getattr(service, k), v)
