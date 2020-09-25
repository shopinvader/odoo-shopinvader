# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time
from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.exceptions import MissingError


class TestProductCommon(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category_products = cls.env["product.category"].create(
            {"name": "Products"}
        )
        # An xmlid on the category is needed
        cls.env["ir.model.data"].create(
            {
                "module": "__test__",
                "name": "category",
                "model": cls.category_products._name,
                "res_id": cls.category_products.id,
            }
        )

        cls.prod_attr = cls.env["product.attribute"].create(
            {"name": "Attribute"}
        )
        cls.prod_attr_start = cls.env["product.attribute.value"].create(
            {"name": "Start", "attribute_id": cls.prod_attr.id}
        )
        cls.prod_attr_king = cls.env["product.attribute.value"].create(
            {"name": "King", "attribute_id": cls.prod_attr.id}
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "default_code": "13579",
                "list_price": 13.95,
                "categ_id": cls.category_products.id,
                "sale_ok": True,
                "type": "product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.prod_attr.id,
                            "value_ids": [
                                (4, cls.prod_attr_start.id),
                                (4, cls.prod_attr_king.id),
                            ],
                        },
                    )
                ],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "default_code": "123",
                "type": "product",
                "list_price": 230.95,
                "categ_id": cls.category_products.id,
                "sale_ok": True,
                "barcode": "code",
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "type": "product",
                "default_code": "321",
                "list_price": 330.95,
                "categ_id": cls.category_products.id,
                "sale_ok": True,
            }
        )
        cls.product_not_for_sale = cls.env["product.product"].create(
            {
                "name": "NotForSale",
                "default_code": "123456",
                "type": "product",
                "list_price": 195,
                "categ_id": cls.category_products.id,
                "sale_ok": False,
            }
        )

    def setUp(self, *args, **kwargs):
        super(TestProductCommon, self).setUp(*args, **kwargs)

        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="stock")

        self._data = {
            "id": self.product_1.id,
            "name": "Product 1",
            "price": "13.95",
            "default_code": "13579",
            "ean": "",
            "xml_id": "",
            "qty_available": "0.000",
            "category": {"id": "__test__.category", "name": "Products"},
            "attributes": [
                {
                    "values": [
                        {"name": "Start", "id": self.prod_attr_start.id},
                        {"name": "King", "id": self.prod_attr_king.id},
                    ],
                    "attribute": {
                        "name": "Attribute",
                        "id": self.prod_attr.id,
                    },
                }
            ],
        }

    def _check_data(self, result, data):
        """Do a deep comaraison of a JSON object."""
        self.assertTrue(set(result.keys()) == set(data.keys()))
        for key in data.keys():
            if isinstance(data[key], dict):
                self._check_data(result[key], data[key])
            if isinstance(data[key], list):
                if len(data[key]) == 1 and len(result[key]) == 1:
                    self._check_data(result[key][0], data[key][0])
                else:
                    self.assertEqual(len(result[key]), len(data[key]))
                    result[key].sort(key=lambda obj: obj["id"])
                    data[key].sort(key=lambda obj: obj["id"])
                    for pos in range(len(result[key])):
                        self._check_data(result[key][pos], data[key][pos])
            else:
                self.assertEqual(result[key], data[key])

    def test_get_all_products(self):
        """Get all salable proudcts, there is 6."""
        res = self.service.dispatch("search", params={"per_page": 10})
        self.assertTrue(len(res["data"]) > 5)

    def test_get_products_from_category(self):
        """Get all product in a category."""
        res = self.service.dispatch(
            "search", params={"category_id": self.category_products.id}
        )
        data = res["data"]
        self.assertEqual(len(data), 5)

    def test_get_products_from_barcode(self):
        """Get all product in a barcode"""
        res = self.service.dispatch("search", params={"ean": "code"})
        data = res["data"]
        self.assertEqual(len(data), 1)

    def test_get_one_product_by_id(self):
        """Get a product by id."""
        res = self.service.dispatch("get", self.product_1.id)
        self._check_data(res, self._data)

    def test_get_product_not_for_sale(self):
        """Get on not salable product, raises not found."""
        with self.assertRaises(MissingError):
            self.service.dispatch("get", self.product_not_for_sale.id)

    @freeze_time("2019-01-01", as_arg=True)
    def test_get_recent_updated_products_01(frozen_time, self):
        """Get all product in a barcode"""
        res = self.service.dispatch(
            "search", params={"date": "01/09/2020 23:00:00"}
        )
        data = res["data"]
        self.assertTrue(len(data), 0)

    @freeze_time("2019-02-02", as_arg=True)
    def test_get_recent_updated_products_02(frozen_time, self):
        self.product_1.write({"name": "Updated name"})
        res = self.service.dispatch(
            "search", params={"date": "01/02/2020 00:00:00"}
        )
        data = res["data"]
        self.assertTrue(len(data), 1)

        res = self.service.dispatch(
            "search", params={"date": "01/01/2019 00:00:00"}
        )
        data = res["data"]
        self.assertTrue(len(data), 5)
