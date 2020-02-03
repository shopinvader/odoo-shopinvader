# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCase


class TestPartnerAccessInfo(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerAccessInfo, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.contact = cls.partner.create(
            {
                "name": "Just an address",
                "type": "contact",
                "parent_id": cls.partner.id,
            }
        )

    def test_access_info_owner1(self):
        with self.backend.work_on(
            "res.partner", partner=self.partner, partner_user=self.partner
        ) as work:
            info = work.component(usage="access.info")

        self.assertTrue(info.is_owner(self.partner.id))

        # on my partner I can RU
        self.assertEqual(
            info.for_profile(self.partner.id),
            {"read": True, "update": True, "delete": False},
        )
        # on my addresses I can RUD
        self.assertEqual(
            info.for_address(self.contact.id),
            {"read": True, "update": True, "delete": True},
        )

    def test_access_info_owner2(self):
        with self.backend.work_on(
            "res.partner", partner=self.partner, partner_user=self.partner
        ) as work:
            info = work.component(usage="access.info")

        self.assertTrue(info.is_owner(self.partner.id))

        # partner is enabled, can do everything
        self.partner.shopinvader_enabled = True
        expected = {
            "addresses": {"create": True},
            "cart": {"add_item": True, "update_item": True},
        }
        self.assertEqual(info.permissions(), expected)

        # partner is disabled, can do nothing
        self.partner.shopinvader_enabled = False
        expected = {
            "addresses": {"create": False},
            "cart": {"add_item": False, "update_item": False},
        }
        self.assertEqual(info.permissions(), expected)

    def test_access_info_non_owner1(self):
        with self.backend.work_on(
            "res.partner", partner=self.partner, partner_user=self.contact
        ) as work:
            info = work.component(usage="access.info")

        self.assertFalse(info.is_owner(self.partner.id))
        self.assertTrue(info.is_owner(self.contact.id))

        # on my partner I can R only
        self.assertEqual(
            info.for_profile(self.partner.id),
            {"read": True, "update": False, "delete": False},
        )
        # on my addresses I can RU only
        self.assertEqual(
            info.for_address(self.contact.id),
            {"read": True, "update": True, "delete": False},
        )

    def test_access_info_non_owner2(self):
        with self.backend.work_on(
            "res.partner", partner=self.partner, partner_user=self.contact
        ) as work:
            info = work.component(usage="access.info")

        self.assertFalse(info.is_owner(self.partner.id))
        self.assertTrue(info.is_owner(self.contact.id))

        # no matter if the partner user is enabled
        self.contact.shopinvader_enabled = True

        # partner is enabled, can do everything
        self.partner.shopinvader_enabled = True
        expected = {
            "addresses": {"create": True},
            "cart": {"add_item": True, "update_item": True},
        }
        self.assertEqual(info.permissions(), expected)

        # partner is disabled, can do nothing
        self.partner.shopinvader_enabled = False
        expected = {
            "addresses": {"create": False},
            "cart": {"add_item": False, "update_item": False},
        }
        self.assertEqual(info.permissions(), expected)
