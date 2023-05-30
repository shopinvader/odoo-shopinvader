# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.fields import first

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopInvaderCustomerService(CommonCase):
    """
    Tests for shopinvader.customer.service
    """

    def setUp(self, *args, **kwargs):
        super(TestShopInvaderCustomerService, self).setUp(*args, **kwargs)
        self.fposition_obj = self.env["account.fiscal.position"]
        self.profile_default_public_tax_inc = self.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_1"
        )
        self.profile_pro_tax_exc = self.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_2"
        )
        self.profile_public_tax_exc = self.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_3"
        )
        # Data to create a shopinvader partner
        self.data = {
            "email": "new@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "external_id": "D5CdkqOEL",
        }
        self.backend.write({"use_sale_profile": True})
        session = self.shopinvader_session
        with self.work_on_services(partner=None, shopinvader_session=session) as work:
            self.service = work.component(usage="customer")

    def _create_partner(self, country, extra=None):
        data = self.data
        if extra:
            data.update(extra)
        data["country"] = {"id": self.env.ref("base.%s" % country).id}
        result = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(result.get("id", False))
        self.assertEqual(partner.email, data.get("email"))
        self.assertEqual(
            partner.shopinvader_bind_ids.external_id, data.get("external_id")
        )
        for key in data:
            if key == "external_id":
                continue
            elif key == "country":
                self.assertEqual(
                    partner.country_id.id, data.get(key, {}).get("id", "t")
                )
            else:
                self.assertEqual(partner[key], data.get(key))
        binded = first(
            partner.shopinvader_bind_ids.filtered(
                lambda s: s.backend_id.id == self.backend.id
            )
        )
        return binded

    def test_create_customer(self):
        """
        Test to create a shopinvader.partner (should also create a res.partner)
        Ensure that the country is correctly set on the partner and the
        profile too
        :return: bool
        """
        shopinvader_partner = self._create_partner("fr")
        self.assertEqual(
            shopinvader_partner.sale_profile_id,
            self.profile_default_public_tax_inc,
        )

    def test_create_customer_business_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner related to a country of a a fiscal
        position of the profile.
        The computation should assign the right profile.
        :return: bool
        """
        shopinvader_partner = self._create_partner("fr", extra={"vat": "BE0477472701"})
        # Note for now we do not have automatic rule to
        # set a specific pricelist depending on vat number
        # so we set it manually
        shopinvader_partner.write(
            {"property_product_pricelist": self.env.ref("shopinvader.pricelist_1").id}
        )
        self.assertEqual(shopinvader_partner.sale_profile_id, self.profile_pro_tax_exc)

    def test_create_customer_exclude_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner related to a country of a a fiscal
        position of the profile.
        The computation should assign the right profile.
        :return: bool
        """
        shopinvader_partner = self._create_partner("us")
        self.assertEqual(
            shopinvader_partner.sale_profile_id, self.profile_public_tax_exc
        )

    def test_create_customer_default_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner without country, vat etc.
        So no fiscal position should be found for this new partner.
        So we check if the default profile is assign to this new partner.
        :return: bool
        """
        # remove the profile tax_exc and create a 'US' partner
        # as they is no more role that match the partner should have
        # the default one
        self.profile_public_tax_exc.unlink()
        shopinvader_partner = self._create_partner("us")
        self.assertEqual(
            shopinvader_partner.sale_profile_id,
            self.profile_default_public_tax_inc,
        )

    def test_create_customer_without_profile(self):
        """
        For this test, we disable automatic assignation of sale profile.
        We ensure that the new partner doesn't have one, after the creation.
        :return: bool
        """
        # Disable auto-assign profile
        self.backend.use_sale_profile = False
        shopinvader_partner = self._create_partner("fr")
        self.assertFalse(shopinvader_partner.sale_profile_id)
