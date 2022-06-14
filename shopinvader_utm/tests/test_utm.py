# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields

from odoo.addons.shopinvader.tests.common import CommonCase


class UtmMixinCase(CommonCase):
    def _create_sale(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.backend.anonymous_partner_id.id,
                "partner_shipping_id": self.backend.anonymous_partner_id.id,
                "partner_invoice_id": self.backend.anonymous_partner_id.id,
                "pricelist_id": self.env["product.pricelist"].browse(1).id,
                "typology": "cart",
                "shopinvader_backend_id": self.backend.id,
                "date_order": fields.Datetime.now(),
                "analytic_account_id": self.backend.account_analytic_id.id,
            }
        )

    def test_add_utm(self):
        sale = self._create_sale()
        self.assertEqual(sale.campaign_id.name, False)
        self.assertEqual(sale.medium_id.name, False)
        self.assertEqual(sale.source_id.name, False)
        params = {
            "campaign": "Christmas Special",
            "medium": "DoesNotExist",
            "source": "Twitter",
        }
        sale.shopinvader_add_utm(params)
        self.assertEqual(sale.campaign_id.name, "Christmas Special")
        self.assertEqual(sale.source_id.name, "Twitter")
        self.assertNotEqual(sale.medium_id.name, "DoesNotExist")
        sale.shopinvader_add_utm({"medium": "Facebook"})
        self.assertEqual(sale.medium_id.name, "Facebook")
