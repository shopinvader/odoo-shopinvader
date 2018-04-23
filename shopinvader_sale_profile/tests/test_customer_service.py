# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.fields import first


class TestShopInvaderCustomerService(CommonCase):
    """
    Tests for shopinvader.customer.service
    """

    def setUp(self, *args, **kwargs):
        super(TestShopInvaderCustomerService, self).setUp(*args, **kwargs)
        self.fposition_obj = self.env['account.fiscal.position']
        self.default_sale_profile = self.env.ref(
            'shopinvader_sale_profile.shopinvader_sale_profile_1')
        self.sale_profile2 = self.env.ref(
            'shopinvader_sale_profile.shopinvader_sale_profile_2')
        self.sale_profile3 = self.env.ref(
            'shopinvader_sale_profile.shopinvader_sale_profile_3')
        # Data to create a shopinvader partner
        self.data = {
            'email': 'new@customer.example.com',
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
        }
        self.backend.write({
            'use_sale_profile': True,
        })
        session = self.shopinvader_session
        with self.work_on_services(partner=None,
                                   shopinvader_session=session) as work:
            self.service = work.component(usage='customer')

    def test_create_customer(self):
        """
        Test to create a shopinvader.partner (should also create a res.partner)
        Ensure that the country is correctly set on the partner and the
        profile too
        :return: bool
        """
        sale_profile = self.default_sale_profile
        country_fr = self.env.ref('base.fr')
        data = self.data
        data.update({
            'external_id': 'D5CdkqOEL',
            'country': {
                'id': country_fr.id,
            },
        })
        result = self.service.dispatch('create', params=data)['data']
        partner = self.env['res.partner'].browse(result.get('id', False))
        self.assertEqual(partner.email, data.get('email'))
        self.assertEqual(
            partner.shopinvader_bind_ids.external_id, data.get('external_id'))
        for key in data:
            if key == 'external_id':
                continue
            elif key == 'country':
                self.assertEqual(
                    partner.country_id.id, data.get(key, {}).get('id', 't'))
            else:
                self.assertEqual(partner[key], data.get(key))
        self.assertEqual(
            partner.shopinvader_bind_ids.sale_profile_id.id, sale_profile.id)
        return True

    def test_create_customer_business_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner related to a country of a a fiscal
        position of the profile.
        The computation should assign the right profile.
        :return: bool
        """
        fposition_obj = self.fposition_obj
        shopinvader_pricelist = self.env.ref('shopinvader.pricelist_1')
        sale_profile = self.sale_profile2
        fiscal_positions = sale_profile.fiscal_position_ids
        backend = self.backend
        data = self.data
        # Pick first country of fiscal position to ensure have a fiscal pos.
        country = first(fiscal_positions.mapped("country_id"))
        if not country:
            country = first(
                fiscal_positions.mapped("country_group_id.country_ids"))
        data.update({
            'email': 'business@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'vat': 'BE0477472701',
            'country': {
                'id': country.id,
            },
        })
        result = self.service.dispatch('create', params=data).get('data', {})
        partner = self.env['res.partner'].browse(result.get('id', False))
        # For this test, we need a fiscal position on the partner created to
        # check if the sale profile is correctly assigned
        # We use fiscal positions defined into demo data of the profile
        fpos_id = fposition_obj.get_fiscal_position(
            partner.id, delivery_id=partner.id)
        self.assertIn(fpos_id, fiscal_positions.ids)
        # Note for now we do not have automatic rule to
        # set a specific pricelist depending on vat number
        # so we set it manually
        partner.write({
            'property_product_pricelist': shopinvader_pricelist.id,
        })
        binded = first(partner.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id.id == backend.id))
        self.assertEqual(binded.sale_profile_id.id, sale_profile.id)
        self.assertEqual(partner.is_company, True)
        return True

    def test_create_customer_exclude_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner related to a country of a a fiscal
        position of the profile.
        The computation should assign the right profile.
        :return: bool
        """
        sale_profile = self.sale_profile3
        fiscal_positions = sale_profile.fiscal_position_ids
        fposition_obj = self.fposition_obj
        backend = self.backend
        data = self.data
        # Pick first country of fiscal position to ensure have a fiscal pos.
        country = first(fiscal_positions.mapped("country_id"))
        if not country:
            country = first(fiscal_positions.mapped(
                "country_group_id.country_ids"))
        data.update({
            'email': 'export@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'phone': '0485485454',
            'country': {
                'id': country.id,
            },
        })
        result = self.service.dispatch('create', params=data).get('data', {})
        partner = self.env['res.partner'].browse(result.get('id', False))
        # For this test, we need a fiscal position on the partner created to
        # check if the sale profile is correctly assigned
        # We use fiscal positions defined into demo data of the profile
        fpos_id = fposition_obj.get_fiscal_position(
            partner.id, delivery_id=partner.id)
        self.assertIn(fpos_id, fiscal_positions.ids)
        binded = first(partner.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id.id == backend.id))
        self.assertEqual(binded.sale_profile_id.id, sale_profile.id)
        return True

    def test_create_customer_default_sale_profile(self):
        """
        Test the assignation of automatic sale profile.
        For this test, we create a partner without country, vat etc.
        So no fiscal position should be found for this new partner.
        So we check if the default profile is assign to this new partner.
        :return: bool
        """
        sale_profile = self.default_sale_profile
        # Ensure this profile is the default
        self.assertTrue(sale_profile.default)
        fposition_obj = self.fposition_obj
        backend = self.backend
        data = self.data
        data.update({
            'email': 'export-default@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'phone': '0485485454',
        })
        result = self.service.dispatch('create', params=data).get('data', {})
        partner = self.env['res.partner'].browse(result.get('id', False))
        # For this test, we need a fiscal position on the partner created to
        # check if the sale profile is correctly assigned
        # We use fiscal positions defined into demo data of the profile
        fpos_id = fposition_obj.get_fiscal_position(
            partner.id, delivery_id=partner.id)
        self.assertFalse(fpos_id)
        binded = first(partner.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id.id == backend.id))
        self.assertEqual(binded.sale_profile_id.id, sale_profile.id)
        return True

    def test_create_customer_without_profile(self):
        """
        For this test, we disable automatic assignation of sale profile.
        We ensure that the new partner doesn't have one, after the creation.
        :return: bool
        """
        # Disable auto-assign profile
        self.backend.write({
            'use_sale_profile': False,
        })
        fiscal_positions = self.env.ref("shopinvader.fiscal_position_2")
        fposition_obj = self.fposition_obj
        backend = self.backend
        data = self.data
        # Pick first country of fiscal position to ensure have a fiscal pos.
        country = first(fiscal_positions.mapped("country_id"))
        if not country:
            country = first(fiscal_positions.mapped(
                "country_group_id.country_ids"))
        data.update({
            'email': 'export-no-profile@customer.example.com',
            'external_id': 'D5CdkqOEL',
            'phone': '0485485454',
            'country': {
                'id': country.id,
            },
        })
        result = self.service.dispatch('create', params=data).get('data', {})
        partner = self.env['res.partner'].browse(result.get('id', False))
        # For this test, we need a fiscal position on the partner created to
        # check if the sale profile is correctly assigned
        # We use fiscal positions defined into demo data of the profile
        fpos_id = fposition_obj.get_fiscal_position(
            partner.id, delivery_id=partner.id)
        self.assertIn(fpos_id, fiscal_positions.ids)
        binded = first(partner.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id.id == backend.id))
        self.assertFalse(binded.sale_profile_id.id)
        return True
