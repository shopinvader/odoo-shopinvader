# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.stock_packaging_calculator.tests.common import TestCommon

from ..schemas import ProductPackaging, ProductProduct, SimpleProductPackaging
from .common import CommonPackagingCase


class TestProductPackagingData(ExtendableMixin, CommonPackagingCase, TestCommon):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.pkg_box.packaging_level_id = (cls.pkg_level_retail_box.id,)
        cls.pkg_big_box.packaging_level_id = (cls.pkg_level_transport_box.id,)
        cls.pkg_pallet.packaging_level_id = (cls.pkg_level_pallet.id,)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.reset_extendable_registry()
        super().tearDownClass()

    def _default_packaging(self):
        return [
            ProductPackaging(
                id=self.pkg_pallet.id,
                name=self.product_a._packaging_name_getter(self.pkg_pallet),
                qty=self.pkg_pallet.qty,
                barcode=self.pkg_pallet.barcode,
                is_unit=False,
                can_be_sold=self.pkg_pallet.can_be_sold,
                contained=[
                    SimpleProductPackaging(
                        id=self.pkg_big_box.id,
                        name=self.product_a._packaging_name_getter(self.pkg_big_box),
                        qty=self.product_a._qty_by_pkg(
                            self.pkg_big_box.qty, self.pkg_pallet.qty
                        )[0],
                        barcode=self.pkg_big_box.barcode,
                        is_unit=False,
                        can_be_sold=self.pkg_big_box.can_be_sold,
                    )
                ],
            ),
            ProductPackaging(
                id=self.pkg_big_box.id,
                name=self.product_a._packaging_name_getter(self.pkg_big_box),
                qty=self.pkg_big_box.qty,
                barcode=self.pkg_big_box.barcode,
                is_unit=False,
                can_be_sold=self.pkg_big_box.can_be_sold,
                contained=[
                    SimpleProductPackaging(
                        id=self.pkg_box.id,
                        name=self.product_a._packaging_name_getter(self.pkg_box),
                        qty=self.product_a._qty_by_pkg(
                            self.pkg_box.qty, self.pkg_big_box.qty
                        )[0],
                        barcode=self.pkg_box.barcode,
                        is_unit=False,
                        can_be_sold=self.pkg_box.can_be_sold,
                    )
                ],
            ),
            ProductPackaging(
                id=self.pkg_box.id,
                name=self.product_a._packaging_name_getter(self.pkg_box),
                qty=self.pkg_box.qty,
                barcode=self.pkg_box.barcode,
                is_unit=False,
                can_be_sold=self.pkg_box.can_be_sold,
                contained=[
                    SimpleProductPackaging(
                        id=self.product_a.uom_id.id,
                        name=self.product_a.uom_id.name,
                        qty=self.product_a._qty_by_pkg(1, self.pkg_box.qty)[0],
                        barcode=None,
                        is_unit=True,
                        can_be_sold=not self.product_a.sell_only_by_packaging,
                    )
                ],
            ),
            ProductPackaging(
                id=self.product_a.uom_id.id,
                name=self.product_a.uom_id.name,
                qty=1,
                barcode=None,
                is_unit=True,
                can_be_sold=not self.product_a.sell_only_by_packaging,
                contained=[],
            ),
        ]

    def test_product_schema(self):
        res = ProductProduct.from_product_product(self.product_a)
        self.assertEqual(len(res.packaging), 4)
        default_packaging = self._default_packaging()
        self.assertEqual(res.packaging, default_packaging)

    def test_shopinvader_display(self):
        self.pkg_big_box.shopinvader_display = False
        res = ProductProduct.from_product_product(self.product_a)
        self.assertEqual(len(res.packaging), 3)
        self.assertNotIn(self.pkg_big_box.id, [pkg.id for pkg in res.packaging])
        # Assert that, as Big Box cannot be displayed,
        # item present in Pallet 'contained' attribute is Box, not Big Box
        pkg_pallet = res.packaging[0]
        self.assertEqual(pkg_pallet.contained[0].id, self.pkg_box.id)

    def test_packaging_can_be_sold(self):
        self.pkg_level_transport_box.can_be_sold = False
        res = ProductProduct.from_product_product(self.product_a)
        default_packaging = self._default_packaging()
        default_packaging[1].can_be_sold = False
        default_packaging[0].contained[0].can_be_sold = False
        self.assertEqual(res.packaging, default_packaging)

    def test_sell_only_by_packaging(self):
        res = ProductProduct.from_product_product(self.product_a)
        self.assertTrue(res.packaging[3].is_unit)
        self.assertTrue(res.packaging[3].can_be_sold)
        self.product_a.sell_only_by_packaging = True
        res = ProductProduct.from_product_product(self.product_a)
        self.assertTrue(res.packaging[3].is_unit)
        self.assertFalse(res.packaging[3].can_be_sold)
