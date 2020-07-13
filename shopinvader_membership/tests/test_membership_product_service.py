# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestMembershipProductService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestMembershipProductService, cls).setUpClass()
        cls.membership_product_obj = cls.env["product.product"]

    def setUp(self, *args, **kwargs):
        super(TestMembershipProductService, self).setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.backend.anonymous_partner_id
        ) as work:
            self.service_guest = work.component(usage="membership_product")

    def _check_data_content(self, data):
        """
        Check data based on given membership products
        :param data: list
        :param membership_products: product.product recordset
        :return: bool
        """
        membership_products = self.membership_product_obj.search(
            [("membership", "=", True)]
        )
        self.assertEquals(len(data), len(membership_products))
        for current_data, membership_product in zip(data, membership_products):
            self.assertEquals(
                current_data.get("name"), membership_product.name
            )
            self.assertEquals(
                current_data.get("default_code") or False,
                membership_product.default_code,
            )
            self.assertEquals(
                current_data.get("description_sale") or False,
                membership_product.description_sale,
            )
            self.assertEquals(
                current_data.get("list_price"), membership_product.list_price
            )

    def test_get_membership_product(self):
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data)
