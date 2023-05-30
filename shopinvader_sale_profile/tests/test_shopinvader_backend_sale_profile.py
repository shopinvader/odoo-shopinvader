# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderBackendSaleProfile(CommonCase):
    """
    Tests for shopinvader.backend w/ sale profile
    """

    def test_get_pricelist_default(self):
        self.assertFalse(self.backend.use_sale_profile)
        expected = self.backend._default_pricelist_id()
        self.assertEqual(self.backend._get_cart_pricelist(), expected)

    def test_compute_pricelist(self):
        self.backend.write({"use_sale_profile": True})
        profile1 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_1")
        profile2 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_2")
        self.assertNotEqual(profile1.pricelist_id, profile2.pricelist_id)
        self.assertTrue(profile1.default)
        expected = profile1.pricelist_id
        self.assertEqual(self.backend.pricelist_id, expected)
        profile1.default = False
        profile2.default = True
        expected = profile2.pricelist_id
        self.assertEqual(self.backend.pricelist_id, expected)

    def test_get_pricelist(self):
        self.backend.write({"use_sale_profile": True})
        profile1 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_1")
        profile2 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_2")
        expected = profile1.pricelist_id
        self.assertEqual(self.backend._get_cart_pricelist(), expected)
        profile1.default = False
        profile2.default = True
        expected = profile2.pricelist_id
        self.assertEqual(self.backend._get_cart_pricelist(), expected)

    def test_get_pricelist_partner_default(self):
        partner = self.env.ref("shopinvader.partner_2")
        expected = self.backend.pricelist_id
        self.assertEqual(self.backend._get_cart_pricelist(partner), expected)

    def test_get_pricelist_partner(self):
        self.backend.write({"use_sale_profile": True})
        profile1 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_1")
        profile2 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_2")
        partner = self.env.ref("shopinvader.partner_2")
        invader_partner = partner._get_invader_partner(self.backend)
        # Ingnore how sale profile is computed, just simulate its value
        with mock.patch.object(
            type(invader_partner),
            "sale_profile_id",
            new_callable=mock.PropertyMock,
        ) as mocked:
            mocked.return_value = profile1
            expected = profile1.pricelist_id
            self.assertEqual(self.backend._get_cart_pricelist(partner), expected)
            mocked.return_value = profile2
            expected = profile2.pricelist_id
            self.assertEqual(self.backend._get_cart_pricelist(partner), expected)

    def test_get_pricelist_partner_no_profile(self):
        self.backend.write({"use_sale_profile": True})
        profile1 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_1")
        profile2 = self.env.ref("shopinvader_sale_profile.shopinvader_sale_profile_2")
        partner = self.env.ref("shopinvader.partner_2")
        invader_partner = partner._get_invader_partner(self.backend)
        # Ingnore how sale profile is computed, just simulate its value
        with mock.patch.object(
            type(invader_partner),
            "sale_profile_id",
            new_callable=mock.PropertyMock,
        ) as mocked:
            mocked.return_value = None
            expected = profile1.pricelist_id
            self.assertEqual(self.backend._get_cart_pricelist(partner), expected)
            profile1.default = False
            profile2.default = True
            expected = profile2.pricelist_id
            self.assertEqual(
                self.backend._get_cart_pricelist(partner),
                expected,
            )
