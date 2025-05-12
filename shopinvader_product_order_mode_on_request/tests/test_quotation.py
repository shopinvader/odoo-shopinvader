# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestQuotation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # as the shop_order_mode is readonly by default except if unabled in the template
        # we need to create the product template first and then get the product variant
        cls.product_quotation_only = (
            cls.env["product.template"]
            .create(
                {"name": "Quotation only Product", "shop_order_mode": "quotation_only"}
            )
            .product_variant_id
        )

        cls.product_direct_sale_only = (
            cls.env["product.template"]
            .create(
                {
                    "name": "Direct sale only Product",
                    "shop_order_mode": "direct_sale_only",
                }
            )
            .product_variant_id
        )

        cls.product_direct_sale_or_quotation = (
            cls.env["product.template"]
            .create(
                {
                    "name": "Direct Sale Or Quotation Product",
                    "shop_order_mode": "direct_sale_or_quotation",
                }
            )
            .product_variant_id
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def test_sale_order_shop_only_quotation(self):
        so = self.env["sale.order"].create(
            {
                "name": "Sale order that should be quotation only",
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_quotation_only.id,
                            "product_uom_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_direct_sale_only.id,
                            "product_uom_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_direct_sale_or_quotation.id,
                            "product_uom_qty": 1,
                        }
                    ),
                ],
            }
        )

        self.assertTrue(so.shop_only_quotation)

        so_2 = self.env["sale.order"].create(
            {
                "name": "Sale order that should NOT be quotation only",
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_direct_sale_only.id,
                            "product_uom_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_direct_sale_or_quotation.id,
                            "product_uom_qty": 1,
                        }
                    ),
                ],
            }
        )

        self.assertFalse(so_2.shop_only_quotation)
