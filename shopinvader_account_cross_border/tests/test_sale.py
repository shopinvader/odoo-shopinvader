# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CrossBorderCommonCase


class SaleCase(CrossBorderCommonCase):
    def setUp(self):
        super(SaleCase, self).setUp()
        self._new_sale()

    def _new_sale(self):
        self.partner = self.env.ref("shopinvader.partner_1")
        vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "shopinvader_backend_id": self.backend.id,
            "user_id": self.env.user.id,
            "pricelist_id": self.ref("product.list0"),
            "typology": "cart",
        }
        self.sale = self.env["sale.order"].create(vals)

    def test_sale(self):
        # Create a sale line
        # Simulate the onchange on the shipping partner and
        # the onchange on fiscal position
        vals = {
            "order_id": self.sale.id,
            "product_id": self.product.id,
            "product_uom_qty": 3.0,
            "product_uom": self.ref("product.product_uom_unit"),
            "price_unit": 800.0,
        }
        line = self.env["sale.order.line"].create(vals)
        self.sale.onchange_partner_shipping_id()
        self.sale._compute_tax_id()
        self.assertEquals(self.sale.fiscal_position_id, self.fiscal_france)
        self.assertEquals(self.tax_france, line.tax_id)
