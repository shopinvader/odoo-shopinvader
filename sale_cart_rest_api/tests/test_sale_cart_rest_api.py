# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSaleCartRestApiCase


class TestSaleCartRestApi(TestSaleCartRestApiCase):
    def test_get_anonymous_no_cart_no_uuid(self):
        with self.cart_service(None) as cart, self.assertEmptyResponse(cart):
            cart.get()

    def test_get_anonymous_no_cart_uuid(self):
        with self.cart_service(None) as cart, self.assertEmptyResponse(cart):
            cart.get(uuid="1234")

    def test_get_anonymous_cart_uuid(self):
        so = self._create_empty_cart(None)
        with self.cart_service(None) as cart:
            self.assertTrue(cart.get(uuid=so.uuid))

    def test_get_anonymous_cart_wrong_uuid(self):
        self._create_empty_cart(None)
        with self.cart_service(None) as cart, self.assertEmptyResponse(cart):
            cart.get(uuid="1234")

    def test_get_authenticated_no_cart_no_uuid(self):
        with self.cart_service(
            self.partner_1.id
        ) as cart, self.assertEmptyResponse(cart):
            cart.get()

    def test_get_authenticated_no_cart_uuid(self):
        with self.cart_service(
            self.partner_1.id
        ) as cart, self.assertEmptyResponse(cart):
            cart.get(uuid="1234")

    def test_get_authenticated_cart_uuid(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            self.assertTrue(cart.get(uuid=so.uuid))

    def test_get_authenticated_cart_wrong_uuid(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            # should return the las open one
            info = cart.get(uuid="1234")
            self.assertTrue(info)
            self.assertEqual(info.get("uuid"), so.uuid)

    def test_get_authenticated_exists_cart_no_uuid(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            # should return the las open one
            info = cart.get()
            self.assertTrue(info)
            self.assertEqual(info.get("uuid"), so.uuid)

    def test_sync_anonymous_no_uuid_no_transactions(self):
        # no uuid and no transaction -> no cart created for anonymous
        with self.cart_service(None) as cart, self.assertEmptyResponse(cart):
            cart.sync(uuid=None, transactions=[])

    def test_sync_anonymous_no_uuid_one_transactions(self):
        # no uuid but at least one transaction -> cart created for anonymous
        with self.cart_service(None) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            so = self.env["sale.order"].browse(info["id"])
            self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_anonymous_uuid_one_transactions(self):
        # uuid but at least one transaction -> cart reused
        with self.cart_service(None) as cart:
            info = cart.sync(
                uuid=self.anonymous_cart.uuid,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            self.assertEqual(self.anonymous_cart.id, info["id"])

    def test_sync_authenticated_no_uuid_one_transactions_no_cart_exists(self):
        # no uuid but at least one transaction and no cart exists-> cart created
        with self.cart_service(self.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            so = self.env["sale.order"].browse(info["id"])
            self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_authenticated_uuid_one_transactions_cart_exists(self):
        # no uuid but at least one transaction and no cart exists-> cart created
        with self.cart_service(self.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            so = self.env["sale.order"].browse(info["id"])
            self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_authenticated_no_uuid_one_transactions_cart_exists(self):
        # no uuid but at least one transaction and cart exists-> cart updated
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            self.assertEqual(so.id, info["id"])
            self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_authenticated_wrong_uuid_one_transactions_cart_exists(self):
        # wrong uuid but at least one transaction and cart exists-> cart updated
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            info = cart.sync(
                uuid="totoid",
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            self.assertEqual(1, len(info["lines"]))
            self.assertEqual(so.id, info["id"])
            self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_transactions(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            line = so.order_line
            self.assertEqual(1, len(line))
            self.assertEqual(self.product_1, line.product_id)
            self.assertEqual(1, line.product_uom_qty)
            # add 3 items to product
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid2",
                        "product_id": self.product_1.id,
                        "qty": 3,
                    }
                ],
            )
            line = so.order_line
            self.assertEqual(1, len(line))
            self.assertEqual(self.product_1, line.product_id)
            self.assertEqual(4, line.product_uom_qty)

            # add remove the line
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid3",
                        "product_id": self.product_1.id,
                        "qty": -5,
                    }
                ],
            )
            line = so.order_line
            self.assertEqual(0, len(line))

    def test_multi_transactions_same_product(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    },
                    {
                        "uuid": "uuid2",
                        "product_id": self.product_1.id,
                        "qty": 3,
                    },
                    {
                        "uuid": "uuid3",
                        "product_id": self.product_1.id,
                        "qty": -1,
                    },
                    {
                        "uuid": "uuid4",
                        "product_id": self.product_1.id,
                        "qty": -1,
                    },
                ],
            )
            line = so.order_line
            self.assertEqual(1, len(line))
            self.assertEqual(self.product_1, line.product_id)
            self.assertEqual(2, line.product_uom_qty)
            self.assertEqual(
                so.applied_transaction_uuids, "uuid1,uuid2,uuid3,uuid4"
            )

    def test_multi_transactions_multi_products_all_create(self):
        so = self._create_empty_cart(self.partner_1.id)
        with self.cart_service(self.partner_1.id) as cart:
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    },
                    {
                        "uuid": "uuid2",
                        "product_id": self.product_2.id,
                        "qty": 3,
                    },
                    {
                        "uuid": "uuid3",
                        "product_id": self.product_1.id,
                        "qty": 3,
                    },
                    {
                        "uuid": "uuid4",
                        "product_id": self.product_2.id,
                        "qty": -1,
                    },
                ],
            )
            lines = so.order_line
            self.assertEqual(2, len(lines))
            line_product_1_id = lines.filtered(
                lambda l, product=self.product_1: l.product_id == product
            )
            self.assertEqual(4, line_product_1_id.product_uom_qty)
            line_product_2_id = lines.filtered(
                lambda l, product=self.product_2: l.product_id == product
            )
            self.assertEqual(2, line_product_2_id.product_uom_qty)
            self.assertEqual(
                so.applied_transaction_uuids, "uuid1,uuid2,uuid3,uuid4"
            )

    def test_multi_transactions_multi_products_mix_create_update(self):
        so = self._create_empty_cart(self.partner_1.id)
        create_line_vals = self.env[
            "sale.order.line"
        ]._transactions_to_record_create(
            so, [{"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1}],
        )
        so.write({"order_line": [create_line_vals]})
        with self.cart_service(self.partner_1.id) as cart:
            cart.sync(
                uuid=so.uuid,
                transactions=[
                    {
                        "uuid": "uuid2",
                        "product_id": self.product_2.id,
                        "qty": 3,
                    },
                    {
                        "uuid": "uuid3",
                        "product_id": self.product_1.id,
                        "qty": 3,
                    },
                    {
                        "uuid": "uuid4",
                        "product_id": self.product_2.id,
                        "qty": -1,
                    },
                ],
            )
            lines = so.order_line
            self.assertEqual(2, len(lines))
            line_product_1_id = lines.filtered(
                lambda l, product=self.product_1: l.product_id == product
            )
            self.assertEqual(4, line_product_1_id.product_uom_qty)
            line_product_2_id = lines.filtered(
                lambda l, product=self.product_2: l.product_id == product
            )
            self.assertEqual(2, line_product_2_id.product_uom_qty)
            self.assertEqual(so.applied_transaction_uuids, "uuid2,uuid3,uuid4")

    def test_cart_validator_response(self):
        with self.cart_service(self.partner_1.id) as cart:
            info = cart.dispatch(
                "sync",
                params=dict(
                    uuid=None,
                    transactions=[
                        {
                            "uuid": "uuid1",
                            "product_id": self.product_1.id,
                            "qty": 1,
                        }
                    ],
                ),
            )
            self.assertTrue(info)
