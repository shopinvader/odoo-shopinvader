# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import wishlist_router


class CommonWishlistCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.not_allowed_partner = cls.env["res.partner"].create(
            {"name": "Test Partner Not Allowed"}
        )
        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
                "groups_id": [(6, 0, [])],
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_security_sale.shopinvader_sale_user_group"
                            ).id,
                            cls.env.ref(
                                "shopinvader_api_wishlist.shopinvader_wishlist_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.partner = partner.with_user(user_with_rights)

        cls.default_fastapi_router = wishlist_router
        cls.prod1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.prod2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.prod3 = cls.env["product.product"].create({"name": "Product 3"})
        cls.prod4 = cls.env["product.product"].create({"name": "Product 4"})
        cls.prod5 = cls.env["product.product"].create({"name": "Product 5"})
        cls.prod6 = cls.env["product.product"].create({"name": "Product 6"})
        cls.wl_params = {
            "name": "My new wishlist :)",
            "ref": "MY_NEW",
            "lines": [
                {"product_id": cls.prod1.id, "quantity": 1.0},
                {"product_id": cls.prod2.id, "quantity": 5.0},
            ],
        }

    def _check_data(self, record, data):
        data_lines = data.pop("lines", [])
        rec_data = record._convert_to_write(record._cache)
        rec_lines = record.set_line_ids
        for key in data:
            self.assertEqual(rec_data[key], data[key])
        for dline in data_lines:
            list_line = rec_lines.filtered(
                lambda x: x.product_id.id == dline["product_id"]
            )
            self.assertTrue(list_line)
            for key in ("quantity", "sequence"):
                if key in dline:
                    self.assertEqual(list_line[key], dline.get(key))
