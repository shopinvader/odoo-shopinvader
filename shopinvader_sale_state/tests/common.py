# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import TransactionCase


class CommonSaleState(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_A, cls.product_B = cls.env["product.product"].create(
            [
                {
                    "name": "Product A",
                    "list_price": 10.0,
                },
                {
                    "name": "Product B",
                    "list_price": 5.0,
                },
            ]
        )
        cls.partner = cls.env["res.partner"].create({"name": "Foo"})
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_A.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_B.id,
                        }
                    ),
                ],
            }
        )
