# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from uuid import uuid4

from requests import Response

from odoo.tests.common import tagged

from ..routers import delivery_router
from .common import TestShopinvaderDeliveryCarrierCommon


@tagged("post_install", "-at_install")
class TestSearchDeliveries(TestShopinvaderDeliveryCarrierCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.carrier = cls.env.ref("delivery.delivery_carrier")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_cust = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env.ref("product.product_product_4")

    def _create_picking(self, partner, sale=False):
        """
        Create a new OUT picking.
        If sale is True, create first a new sale order and generate the picking
        from it.
        (if the picking doesn't come from a sale, it's not returned by service)
        :param partner: res.partner
        :param sale: bool
        :return: stock.picking recordset
        """
        if sale:
            sale_order = self.env.ref("sale.sale_order_4").copy()
            sale_order.write(
                {
                    "partner_id": partner.id,
                    "partner_shipping_id": partner.id,
                }
            )
            sale_order.action_confirm()
            return sale_order.picking_ids
        picking_out = self.env["stock.picking"].create(
            {
                "partner_id": partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_cust.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 3,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_cust.id,
            }
        )
        return picking_out

    def _fill_picking_optional_values(self, pickings):
        """
        Fill some optional values for given pickings
        :param pickings: stock.picking
        :return: bool
        """
        for picking in pickings:
            picking.write(
                {
                    "carrier_id": self.carrier.id,
                    "carrier_tracking_ref": str(uuid4()),
                }
            )
        return True

    def _check_data_content(self, data, pickings):
        """
        Check data based on given pickings
        :param data: list
        :param pickings: stock.picking recordset
        :return: bool
        """
        # To have them into correct order
        pickings = pickings.search([("id", "in", pickings.ids)])
        self.assertEqual(len(data), len(pickings))
        for current_data, picking in zip(data, pickings):
            carrier_dict = current_data.get("carrier")
            sale_id = current_data.get("sale_id")
            self.assertEqual(current_data.get("delivery_id"), picking.id)
            self.assertEqual(current_data.get("name"), picking.name)
            self.assertEqual(
                current_data.get("tracking_reference"),
                picking.carrier_tracking_ref or None,
            )
            if picking.carrier_id:
                self.assertEqual(carrier_dict.get("name"), picking.carrier_id.name)
            else:
                self.assertFalse(carrier_dict)
            if picking.sale_id:
                self.assertEqual(picking.sale_id.id, sale_id)
            else:
                self.assertFalse(sale_id)
            if picking.date_done:
                self.assertEqual(picking.date_done, current_data.get("delivery_date"))
            elif picking.scheduled_date:
                self.assertEqual(
                    picking.scheduled_date,
                    datetime.strptime(
                        current_data["delivery_date"], "%Y-%m-%dT%H:%M:%S"
                    ),
                )
            else:
                self.assertFalse(current_data.get("delivery_date"))
        return True

    def test_get_picking_logged_without_sale(self):
        """
        Test to get all pickings of a logged user.
        1. the user shouldn't have any picking.
        2. Create a picking related to the partner.
           -> The user should have one picking.
        """
        # 1.
        with self._create_test_client(router=delivery_router) as test_client:
            response: Response = test_client.get("/deliveries")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self.assertEqual(info["count"], 0)
        self.assertEqual(info["items"], [])

        # 2.
        picking = self._create_picking(self.partner, sale=True)
        with self._create_test_client(router=delivery_router) as test_client:
            response: Response = test_client.get("/deliveries")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        data = info.get("items", [])
        self._check_data_content(data, picking)
        # Write some optional fields and re-check
        self._fill_picking_optional_values(picking)
        with self._create_test_client(router=delivery_router) as test_client:
            response: Response = test_client.get("/deliveries")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        data = info.get("items", [])
        self._check_data_content(data, picking)

    def test_get_multi_picking(self):
        """
        Test the get on a logged user.
        Create 4 pickings for this user.
        """
        picking1 = self._create_picking(self.partner, sale=True)
        picking2 = self._create_picking(self.partner, sale=True)
        picking3 = self._create_picking(self.partner, sale=True)
        picking4 = self._create_picking(self.partner, sale=True)
        pickings = picking1 | picking2 | picking3 | picking4
        with self._create_test_client(router=delivery_router) as test_client:
            response: Response = test_client.get("/deliveries")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self._check_data_content(info["items"], pickings)
        # Write some optional fields and re-check
        with self._create_test_client(router=delivery_router) as test_client:
            response: Response = test_client.get("/deliveries")
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self._check_data_content(info["items"], pickings)
