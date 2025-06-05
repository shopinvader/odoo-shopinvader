# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.shopinvader_anonymous_partner.models.cookie_helper import COOKIE_NAME


class PartnerPromotionCase(BaseCommon):
    def test_cart_transfer_at_promotion(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        anonymous_partner = cookie_helper._create_anonymous_partner__cookie(
            mock.MagicMock()
        )
        product = self.env["product.product"].create(
            {"name": "product", "uom_id": self.env.ref("uom.product_uom_unit").id}
        )
        anonymous_cart = self.env["sale.order"].create(
            {
                "partner_id": anonymous_partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 1}),
                ],
                "typology": "cart",
            }
        )

        partner = self.env["res.partner"].create(
            {"name": "Test promotion partner", "email": "test+promotion@example.com"}
        )

        cookie_helper._promote_anonymous_partner_and_delete_cookie(
            partner,
            cookies={COOKIE_NAME: anonymous_partner.anonymous_token},
            response=mock.MagicMock(),
        )

        self.assertFalse(anonymous_partner.exists())
        self.assertFalse(anonymous_cart.exists())
        cart = self.env["sale.order"].search([("partner_id", "=", partner.id)])
        self.assertEqual(len(cart.order_line), 1)
        self.assertEqual(cart.order_line[0].product_id, product)
