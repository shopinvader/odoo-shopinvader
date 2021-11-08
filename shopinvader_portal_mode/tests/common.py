# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class PortalModeCommonCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.shop_sales = cls.env.ref("shopinvader.sale_order_2")
        cls.shop_sales += cls.shop_sales.copy()
        cls.shop_sales.action_confirm()
        cls.shop_sales.write(
            {"typology": "sale", "shopinvader_backend_id": cls.backend.id}
        )
        cls.product = cls.env.ref("product.product_product_11")
        cls.non_shop_sales = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    ),
                ],
            }
        )
        cls.draft_order = cls.non_shop_sales.copy()
        cls.non_shop_sales += cls.non_shop_sales.copy()
        cls.non_shop_sales.action_confirm()

    def _get_service(self, usage):
        work_ctx = dict(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        )
        with self.work_on_services(**work_ctx) as work:
            return work.component(usage)
