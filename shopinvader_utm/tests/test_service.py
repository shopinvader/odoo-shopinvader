# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.shopinvader.tests.common import CommonCase


class UtmServiceCase(CommonCase):
    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=None,
            shopinvader_session=self.shopinvader_session,
            utm={
                "campaign": "Christmas Special",
                "medium": "Facebook",
                "source": "Twitter",
            },
        ) as work:
            self.service = work.component(usage="cart")

    def test_service(self):
        res = self.service.dispatch("add_item", params={"product_id": 6, "item_qty": 1})
        record = self.env["sale.order"].browse(res["data"]["id"])
        self.assertEqual(record.campaign_id.name, "Christmas Special")
        self.assertEqual(record.medium_id.name, "Facebook")
        self.assertEqual(record.source_id.name, "Twitter")
