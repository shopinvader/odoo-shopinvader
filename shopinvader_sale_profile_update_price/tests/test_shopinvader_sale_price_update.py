# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_sale import CommonSaleCase


class TestShopinvaderSalePriceUpdate(CommonSaleCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_1 = cls.env.ref("product.product_product_24")
        cls.line = cls.env.ref("shopinvader.sale_order_line_4")
        cls.sale_profile = cls.env.ref(
            "shopinvader_sale_profile.shopinvader_sale_profile_3"
        )

    def _create_pricelists(self, fixed_price, reduction):
        """
        Create 2 new pricelists (one with a fixed price) and another
        (based on the first) with the given reduction.
        :param fixed_price: float
        :param reduction: float
        :return: bool
        """
        pricelist_values = {
            "name": "Custom pricelist 1",
            "discount_policy": "with_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "fixed",
                        "fixed_price": fixed_price,
                    },
                )
            ],
        }
        self.first_pricelist = self.env["product.pricelist"].create(pricelist_values)
        return True

    def test_get_sale_pricelist(self):
        """
        Ensure the _get_sale_pricelist() use the pricelist set on the sale_profile (if set)
        """
        # Let the user to set some discount if necessary
        self.env.ref("product.group_discount_per_so_line").write(
            {"users": [(4, self.env.user.id, False)]}
        )
        fixed_price = 650
        reduction = -100
        self._create_pricelists(fixed_price, reduction)
        self.sale_profile.write({"pricelist_id": self.first_pricelist.id})
        sale_order = self.line.order_id
        shop_partner = sale_order.partner_id.shopinvader_bind_ids.filtered(
            lambda s: s.backend_id == self.backend
        )
        shop_partner.write({"sale_profile_id": self.sale_profile.id})
        self.assertEqual(self.first_pricelist, sale_order._get_sale_pricelist())
        shop_partner.write({"sale_profile_id": False})
        self.assertEqual(
            sale_order.shopinvader_backend_id.pricelist_id,
            sale_order._get_sale_pricelist(),
        )
