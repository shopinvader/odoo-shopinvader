# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from dateutil import parser
from odoo import fields
from odoo.addons.shopinvader.tests.common import CommonCase, CommonTestDownload


class TestDeliveryService(CommonCase, CommonTestDownload):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryService, cls).setUpClass()
        cls.picking_obj = cls.env["stock.picking"]
        cls.move_obj = cls.env["stock.move"]
        cls.partner = cls.env.ref("base.res_partner_2").copy()
        cls.product = cls.env.ref("product.product_product_4")
        cls.carrier = cls.env.ref("delivery.delivery_carrier")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_cust = cls.env.ref("stock.stock_location_customers")
        cls.precision = 2
        cls.backend.delivery_order_states = ""
        cls._create_invader_partner(
            cls.env, record_id=cls.partner.id, external_id=cls.partner.id
        )

    def setUp(self, *args, **kwargs):
        super(TestDeliveryService, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="delivery")
        with self.work_on_services(
            partner=self.backend.anonymous_partner_id
        ) as work:
            self.service_guest = work.component(usage="delivery")

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
            carrier_dict = current_data.get("carrier", {})
            sale_dict = current_data.get("sale", {})
            self.assertEqual(current_data.get("delivery_id"), picking.id)
            self.assertEqual(
                current_data.get("tracking_reference"),
                picking.carrier_tracking_ref or None,
            )
            if picking.carrier_id:
                self.assertEqual(
                    carrier_dict.get("name"), picking.carrier_id.name
                )
            else:
                self.assertFalse(carrier_dict)
            if picking.sale_id:
                self.assertEqual(sale_dict.get("state"), picking.sale_id.state)
                self.assertAlmostEqual(
                    sale_dict.get("amount_total"),
                    picking.sale_id.amount_total,
                    places=self.precision,
                )
                serv_date_order_string = fields.Datetime.to_string(
                    parser.parse(sale_dict.get("date_order"))
                )
                date_order_ts = fields.Datetime.context_timestamp(
                    picking, picking.sale_id.date_order
                )
                self.assertEqual(
                    serv_date_order_string,
                    fields.Datetime.to_string(date_order_ts),
                )
                self.assertEquals(sale_dict.get("sale_id"), picking.sale_id.id)
                self.assertEquals(sale_dict.get("name"), picking.sale_id.name)
            else:
                self.assertFalse(sale_dict)
        return True

    def _create_picking(self, partner=False, sale=False):
        """
        Create a new OUT picking.
        If sale is True, create first a new sale order and generate the picking
        from it.
        (if the picking doesn't come from a sale, it's not returned by service)
        :param partner: res.partner
        :param sale: bool
        :return: stock.picking recordset
        """
        partner = partner or self.partner
        if sale:
            sale_order = self.env.ref("sale.sale_order_4").copy()
            sale_order.write(
                {
                    "partner_id": partner.id,
                    "partner_shipping_id": partner.id,
                    "shopinvader_backend_id": self.backend.id,
                }
            )
            sale_order.action_confirm()
            return sale_order.picking_ids
        picking_out = self.picking_obj.create(
            {
                "partner_id": partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_cust.id,
            }
        )
        self.move_obj.create(
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

    def test_get_picking_anonymous(self):
        """
        Test the get on guest mode (using anonymous user).
        It should return any result, even if the anonymous user has some
        picking out
        :return:
        """
        # Check first without picking related to the anonymous user
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a picking related to the anonymous user
        picking = self._create_picking(
            partner=self.backend.anonymous_partner_id
        )
        self.assertEqual(picking.partner_id, self.backend.anonymous_partner_id)
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)

    def test_get_picking_logged_without_sale(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any picking.
        But to the second, he should have one.
        :return:
        """
        # Check first without picking related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a picking related to the partner
        picking = self._create_picking(partner=self.service.partner, sale=True)
        self.assertEqual(picking.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, picking)
        # Write some optional fields and re-check
        self._fill_picking_optional_values(picking)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, picking)

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

    def test_get_picking_logged_with_sale(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any picking.
        But to the second, he should have one.
        :return:
        """
        # Check first without picking related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a picking related to partner
        picking = self._create_picking(partner=self.service.partner, sale=True)
        self.assertEqual(picking.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, picking)
        # Write some optional fields and re-check
        self._fill_picking_optional_values(picking)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, picking)

    def test_get_multi_picking(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any picking.
        But to the second, he should have one.
        :return:
        """
        picking1 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        picking2 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        picking3 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        picking4 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        pickings = picking1 | picking2 | picking3 | picking4
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, pickings)
        # Write some optional fields and re-check
        self._fill_picking_optional_values(pickings)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, pickings)

    def test_get_multi_picking_no_state_match(self):
        self.backend.delivery_order_states = "assigned|done"
        picking1 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        picking2 = self._create_picking(
            partner=self.service.partner, sale=True
        )
        pickings = picking1 | picking2
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, pickings.browse())
        picking1.state = "done"
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, picking1)

    def test_picking_download(self):
        """
        Data
            * A target with a valid state
        Case:
            * Try to download the document
        Expected result:
            * An http response with the file to download
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        picking = self._create_picking(partner=self.service.partner, sale=True)
        self.assertEqual(picking.state, "confirmed")
        self._test_download_allowed(self.service, picking)

    def test_picking_download_failed(self):
        """
        Data
            * A picking into an invalid/not allowed state
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        :param service: shopinvader service
        :param target: recordset
        :return:
        """
        picking = self._create_picking(
            partner=self.service.partner, sale=False
        )
        self.assertEqual(picking.state, "draft")
        self._test_download_not_allowed(self.service, picking)
