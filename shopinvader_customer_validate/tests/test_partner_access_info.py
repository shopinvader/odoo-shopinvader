# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.common import CommonCase


class TestPartnerAccessInfo(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.invader_partner = cls.partner._get_invader_partner(cls.backend)
        cls.invader_contact = cls._create_invader_partner(
            cls.env,
            name="Just A User",
            parent_id=cls.partner.id,
            email="just@auser.com",
        )
        cls.contact = cls.invader_contact.record_id

    def test_access_info_owner2(self):
        with self.backend.work_on(
            "res.partner",
            partner=self.partner,
            partner_user=self.partner,
            invader_partner=self.invader_partner,
            invader_partner_user=self.invader_partner,
        ) as work:
            info = work.component(usage="access.info")

        self.assertTrue(info.is_owner(self.partner.id))

        # partner is enabled, can do everything
        self.invader_partner.state = "active"
        expected = {
            "addresses": {"create": True},
            "cart": {"add_item": True, "update_item": True},
        }
        perms = info.permissions()
        # Other modules might add other keys: let's compare them atomically.
        for k, v in expected.items():
            self.assertEqual(perms[k], v)

        # partner is disabled, can do nothing
        self.invader_partner.state = "inactive"
        expected = {
            "addresses": {"create": False},
            "cart": {"add_item": False, "update_item": False},
        }
        perms = info.permissions()
        # Other modules might add other keys: let's compare them atomically.
        for k, v in expected.items():
            self.assertEqual(perms[k], v)

    def test_access_info_non_owner2(self):
        with self.backend.work_on(
            "res.partner",
            partner=self.partner,
            invader_partner=self.invader_partner,
            partner_user=self.contact,
            invader_partner_user=self.invader_contact,
        ) as work:
            info = work.component(usage="access.info")

        self.assertFalse(info.is_owner(self.partner.id))
        self.assertTrue(info.is_owner(self.contact.id))

        # no matter if the partner user is enabled
        self.invader_contact.state = "active"

        # partner is enabled, can do everything
        self.invader_partner.state = "active"
        expected = {
            "addresses": {"create": True},
            "cart": {"add_item": True, "update_item": True},
        }
        perms = info.permissions()
        for k, v in expected.items():
            self.assertEqual(perms[k], v)
        # partner is disabled, can do nothing
        self.invader_partner.state = "inactive"
        expected = {
            "addresses": {"create": False},
            "cart": {"add_item": False, "update_item": False},
        }
        perms = info.permissions()
        for k, v in expected.items():
            self.assertEqual(perms[k], v)
