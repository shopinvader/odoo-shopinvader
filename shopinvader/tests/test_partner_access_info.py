# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCase


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

    def test_access_info_owner1(self):
        with self.backend.work_on(
            "res.partner",
            partner=self.partner,
            partner_user=self.partner,
            invader_partner=self.invader_partner,
            invader_partner_user=self.invader_partner,
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

    def test_access_info_non_owner1(self):
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
