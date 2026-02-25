# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestShopinvaderSaleChannelCart(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale_channel = cls.env["sale.channel"].create(
            {
                "name": "Test Sale Channel",
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
            }
        )

    def test_normal_partner_creation_pricelist(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.assertNotEqual(partner.property_product_pricelist, self.pricelist)

    def test_partner_creation_from_sale_channel_pricelist(self):
        self.sale_channel.partner_pricelist_id = self.pricelist
        partner = (
            self.env["res.partner"]
            .with_context(sale_channel_id=self.sale_channel.id)
            .create(
                {
                    "name": "Test Partner",
                }
            )
        )
        self.assertEqual(partner.property_product_pricelist, self.pricelist)
