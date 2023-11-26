# Copyright 2023 ACSONE SA/NV (https://acsone.eu).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ..schemas import Sale, SaleSearch
from .common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def test_sale_from_sale_order(self):
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.id, self.sale_order.id)
        self.assertEqual(sale.state, self.sale_order.shopinvader_state)
        self.assertEqual(sale.name, self.sale_order.name)
        self.assertEqual(sale.client_order_ref, "client ref")
        self.assertEqual(sale.date_order, self.sale_order.date_order)
        self.assertEqual(sale.date_commitment, None)
        self.assertEqual(sale.typology, self.sale_order.typology)
        self.assertEqual(sale.note, "<p>note</p>")
        self.assertEqual(len(sale.lines), 1)
        self.assertEqual(sale.lines[0].id, self.sale_order.order_line[0].id)
        self.assertEqual(sale.lines[0].qty, 1)

    def test_domain_from_sale_search(self):
        search = SaleSearch(name="test")
        domain = search.to_odoo_domain(self.env)
        self.assertIn(("name", "ilike", "test"), domain)
