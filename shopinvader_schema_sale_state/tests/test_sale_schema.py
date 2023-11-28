# Copyright 2023 ACSONE SA/NV (https://acsone.eu).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def test_sale_from_sale_order(self):
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.state, self.sale_order.shopinvader_state)
