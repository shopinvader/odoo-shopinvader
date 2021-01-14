# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo.addons.shopinvader_wishlist.tests.test_wishlist import (
    CommonWishlistCase,
)

MOD_PATH = "odoo.addons.shopinvader_locomotive_wishlist"
MOCK_PATH = (
    MOD_PATH + ".components.event_listeners.ShopinvaderWishlistListener"
)


class TestWishlistCase(CommonWishlistCase):
    """Make sure our event listener is called.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    @mock.patch(MOCK_PATH + "._export_partner_info")
    def test_replace_items(self, mocked_export_partner_info):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        prod1 = self.prod_set.set_line_ids[0].product_id
        prod2 = self.prod_set.set_line_ids[1].product_id
        prod3 = self.prod_set.set_line_ids[2].product_id
        self.wishlist_service.dispatch(
            "replace_items",
            self.prod_set.id,
            params={
                "lines": [
                    {
                        "product_id": prod1.id,
                        "replacement_product_id": self.prod3.id,
                    },
                    {
                        "product_id": prod2.id,
                        "replacement_product_id": self.prod4.id,
                    },
                    {
                        "product_id": prod3.id,
                        "replacement_product_id": self.prod5.id,
                    },
                ]
            },
        )
        mocked_export_partner_info.assert_called_with(
            self.prod_set, fields=None
        )
        self.assertIn(
            "_force_export",
            mocked_export_partner_info.call_args[0][0].env.context,
        )
