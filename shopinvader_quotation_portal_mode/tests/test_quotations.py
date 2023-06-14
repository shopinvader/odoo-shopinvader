# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_portal_mode.tests.common import PortalModeCommonCase


class ShopinvaderCartQuotationCase(PortalModeCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.sale_order_portal_mode = True
        cls.non_shop_quotations = cls.draft_order.copy() | cls.draft_order.copy()
        cls.shop_quotations = cls.draft_order.copy() | cls.draft_order.copy()
        cls.shop_quotations.shopinvader_backend_id = cls.backend
        cls.quotations = cls.shop_quotations | cls.non_shop_quotations
        cls.quotations.action_quotation_sent()

    def setUp(self):
        super().setUp()
        self.service = self._get_service("quotations")

    def test_quotation_portal_mode(self):
        res = self.service.dispatch("search")
        self.assertEqual(set(self.quotations.ids), {x["id"] for x in res["data"]})

    def test_quotation_portal_mode_disabled(self):
        self.backend.sale_order_portal_mode = False
        res = self.service.dispatch("search")
        self.assertEqual(set(self.shop_quotations.ids), {x["id"] for x in res["data"]})

    def test_confirm_from_shop(self):
        order = self.non_shop_quotations[0]
        self.service.dispatch("confirm", order.id)
        self.assertEqual(order.typology, "sale")
        self.assertEqual(order.shopinvader_backend_id, self.backend)
