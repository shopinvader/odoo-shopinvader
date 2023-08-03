# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_base.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase):
    def setUp(self):
        super().setUp()
        # TODO: This should be in setUpClass, but that should be changed
        # in shopinvader's CommonConnectedCartCase first
        # Configure multiple taxes on a sale order
        self.tax_10 = self.env.ref("shopinvader_sale_amount_by_group.tax_10")
        self.tax_20 = self.env.ref("shopinvader_sale_amount_by_group.tax_20")
        self.cart.order_line[0].tax_id = [(6, 0, self.tax_10.ids)]
        self.cart.order_line[1].tax_id = [(6, 0, self.tax_20.ids)]

    def test_cart(self):
        data = self.service.dispatch("update", params=dict())["data"]
        # Test that groups are returned in the same order than amount_by_group
        # which is respecting tax groups' sequences and how they should be printed
        res = data["amount"]["amount_by_group"]
        for group, res_group in zip(self.cart.amount_by_group, res):
            self.assertEqual(group[0], res_group["name"])
            self.assertEqual(group[1], res_group["amount"])
            self.assertEqual(group[2], res_group["base"])
            # Also test types, in case upstream changes amount_by_group return order
            self.assertIs(type(res_group["name"]), str)
            self.assertIs(type(res_group["amount"]), float)
            self.assertIs(type(res_group["base"]), float)
        # Test that the total tax amount matches the order's tax amount
        # It's not the scope of this module to compute it, but this way we make sure
        # we're properly converting the in amount_by_group values list to a dict.
        tax_amount = sum([g["amount"] for g in res])
        self.assertEqual(tax_amount, self.cart.amount_tax)
