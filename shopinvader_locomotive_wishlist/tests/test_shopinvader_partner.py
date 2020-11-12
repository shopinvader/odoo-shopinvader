# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo.addons.shopinvader_locomotive.tests.test_shopinvader_partner import (
    CommonShopinvaderPartner,
)

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestShopinvaderWishlistSync(CommonShopinvaderPartner):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderWishlistSync, cls).setUpClass()
        # recreate all records to make sure there's isolation
        cls.partner1 = cls.env["shopinvader.partner"].create(
            {
                "name": "John",
                "email": "john@test.com",
                "backend_id": cls.backend.id,
                "external_id": "john",
            }
        )
        cls.partner2 = cls.env["shopinvader.partner"].create(
            {
                "name": "Mike",
                "email": "mike@test.com",
                "backend_id": cls.backend.id,
                "external_id": "mike",
            }
        )
        cls.prod_set1 = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set1.with_context(connector_no_export=True).write(
            {
                "set_line_ids": [(5, 0, 0)],
                "shopinvader_backend_id": cls.backend.id,
                "partner_id": cls.partner1.record_id.id,
            }
        )
        cls.prod_set2 = (
            cls.prod_set1.with_context(connector_no_export=True)
            .copy({"name": "List 2"})
            .with_context(connector_no_export=None)
        )
        cls.prod1 = cls.env["product.product"].create({"name": "P1"})
        cls.prod2 = cls.env["product.product"].create({"name": "P2"})
        cls.prod3 = cls.env["product.product"].create({"name": "P3"})
        cls._bind_products(
            cls, cls.prod1 + cls.prod2 + cls.prod3, backend=cls.backend
        )

    def test_create_wishlist(self):
        partner_binding = self.partner2
        partner = self.partner2.record_id
        self._init_job_counter()
        prod_set3 = self.env["product.set"].create(
            {
                "name": "List 3",
                "partner_id": partner.id,
                "shopinvader_backend_id": self.backend.id,
                "set_line_ids": [
                    (0, 0, {"product_id": self.prod1.id, "quantity": 1}),
                    (0, 0, {"product_id": self.prod2.id, "quantity": 1}),
                ],
            }
        )
        self._check_nbr_job_created(3)

        with requests_mock.mock() as m:
            m.post(
                self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"}
            )
            m.put(
                self.base_url
                + "/content_types/customers/entries/"
                + partner_binding.external_id,
                json={},
            )
            # export ran as demo user even if no access on shopinvader_partner
            self._perform_created_job()
            data = m.request_history[1].json()["content_entry"]
            expected_wl = {
                str(prod_set3.id): {"id": prod_set3.id, "name": prod_set3.name}
            }
            expected_prods = {
                str(self.prod1.id): [prod_set3.id],
                str(self.prod2.id): [prod_set3.id],
            }
            self.assertEqual(json.loads(data["wishlists"]), expected_wl)
            self.assertEqual(
                json.loads(data["product_wishlists"]), expected_prods
            )

    def test_update_wishlist(self):
        self._init_job_counter()
        # add new products
        self.prod_set1.write(
            {
                "set_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_set_id": self.prod_set1.id,
                            "product_id": self.prod2.id,
                            "quantity": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_set_id": self.prod_set1.id,
                            "product_id": self.prod3.id,
                            "quantity": 1,
                        },
                    ),
                ]
            }
        )
        self.prod_set2.write(
            {
                "set_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_set_id": self.prod_set2.id,
                            "product_id": self.prod3.id,
                            "quantity": 1,
                        },
                    )
                ]
            }
        )
        self._check_nbr_job_created(3)
        expected_wl = {
            str(self.prod_set1.id): {
                "id": self.prod_set1.id,
                "name": self.prod_set1.name,
            },
            str(self.prod_set2.id): {
                "id": self.prod_set2.id,
                "name": self.prod_set2.name,
            },
        }
        expected_prods = {
            str(self.prod2.id): [self.prod_set1.id],
            str(self.prod3.id): [self.prod_set1.id, self.prod_set2.id],
        }
        self._test_export(self.partner1, expected_wl, expected_prods)

        # another round: add prod1 to set2
        self._init_job_counter()
        self.prod_set2.write(
            {
                "set_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_set_id": self.prod_set2.id,
                            "product_id": self.prod1.id,
                            "quantity": 1,
                        },
                    )
                ]
            }
        )
        self._check_nbr_job_created(1)
        expected_prods = {
            str(self.prod1.id): [self.prod_set2.id],
            str(self.prod2.id): [self.prod_set1.id],
            str(self.prod3.id): [self.prod_set1.id, self.prod_set2.id],
        }
        self._test_export(self.partner1, expected_wl, expected_prods)

    def _test_export(self, partner_binding, expected_wl, expected_prods):
        with requests_mock.mock() as m:
            m.post(
                self.base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"}
            )
            m.put(
                self.base_url
                + "/content_types/customers/entries/"
                + partner_binding.external_id,
                json={},
            )
            # export ran as demo user even if no access on shopinvader_partner
            self._perform_created_job()
            data = m.request_history[1].json()["content_entry"]

            self.assertEqual(json.loads(data["wishlists"]), expected_wl)
            self.assertEqual(
                json.loads(data["product_wishlists"]), expected_prods
            )

    def test_create_line_directly(self):
        self._init_job_counter()
        self.env["product.set.line"].create(
            {
                "product_set_id": self.prod_set2.id,
                "product_id": self.prod1.id,
                "quantity": 1,
            }
        )
        self.env["product.set.line"].create(
            {
                "product_set_id": self.prod_set1.id,
                "product_id": self.prod3.id,
                "quantity": 1,
            }
        )
        self._check_nbr_job_created(2)
        expected_wl = {
            str(self.prod_set1.id): {
                "id": self.prod_set1.id,
                "name": self.prod_set1.name,
            },
            str(self.prod_set2.id): {
                "id": self.prod_set2.id,
                "name": self.prod_set2.name,
            },
        }
        expected_prods = {
            str(self.prod1.id): [self.prod_set2.id],
            str(self.prod3.id): [self.prod_set1.id],
        }
        self._test_export(self.partner1, expected_wl, expected_prods)

    def test_delete_line_directly(self):
        set_line = self.env["product.set.line"].create(
            {
                "product_set_id": self.prod_set1.id,
                "product_id": self.prod3.id,
                "quantity": 1,
            }
        )
        self._init_job_counter()
        set_line.unlink()
        self._check_nbr_job_created(1)
        expected_wl = {
            str(self.prod_set1.id): {
                "id": self.prod_set1.id,
                "name": self.prod_set1.name,
            },
            str(self.prod_set2.id): {
                "id": self.prod_set2.id,
                "name": self.prod_set2.name,
            },
        }
        expected_prods = {}
        self._test_export(self.partner1, expected_wl, expected_prods)
