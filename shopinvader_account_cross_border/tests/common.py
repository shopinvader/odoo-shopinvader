# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.common import CommonCase


class CrossBorderCommonCase(CommonCase):
    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"][
            "cart_id"
        ]
        self.assertEqual(response["store_cache"], {"cart": response["data"]})
        return response["data"]

    def add_item(self, product_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "add_item", params={"product_id": product_id, "item_qty": qty}
            )
        )

    @classmethod
    def _create_fiscal_position(cls):
        cls.france = cls.env.ref("base.fr")
        cls.fiscal_position_tax_model = cls.env["account.fiscal.position.tax"]
        cls.tax_model = cls.env["account.tax"]
        vals = {"name": "Cross Border France"}
        cls.fiscal_france = cls.env["account.fiscal.position"].create(vals)
        cls.local_tax = cls.env["account.tax"].search(
            [("type_tax_use", "=", "sale"), ("price_include", "=", True)],
            limit=1,
        )

        cls.tax_france = cls.tax_model.create(
            dict(
                name="Include tax",
                amount="20.00",
                price_include=True,
                type_tax_use="sale",
            )
        )

        cls.tax_fiscal_position_fr = cls.fiscal_position_tax_model.create(
            dict(
                position_id=cls.fiscal_france.id,
                tax_src_id=cls.local_tax.id,
                tax_dest_id=cls.tax_france.id,
            )
        )

    def _add_tax_mapping(self):
        self.backend.write(
            {
                "tax_mapping_ids": [
                    (
                        0,
                        0,
                        {
                            "country_id": self.france.id,
                            "fiscal_position_id": self.fiscal_france.id,
                        },
                    )
                ]
            }
        )

    def _assign_product_tax(self):
        self.product.taxes_id = self.local_tax

    @classmethod
    def setUpClass(cls):
        super(CrossBorderCommonCase, cls).setUpClass()
        cls.product = cls.env.ref("product.product_product_24")
        cls._create_fiscal_position()

    def setUp(self):
        super(CrossBorderCommonCase, self).setUp()
        self._add_tax_mapping()
        self._assign_product_tax()
