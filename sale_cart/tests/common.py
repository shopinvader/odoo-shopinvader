# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class SaleCartCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(SaleCartCommon, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.so_cart = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {"product_id": cls.product.id, "product_uom_qty": 1},
                    )
                ],
                "typology": "cart",
            }
        )
