# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>

from odoo.tests import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas.category import ProductCategory


class TestShopinvaderCategoryBase(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cat_obj = cls.env["product.category"]

        cls.cat_level1 = cat_obj.create({"name": "Category Level 1"})
        cls.cat_level2 = cat_obj.create(
            {"name": "Category Level 2", "parent_id": cls.cat_level1.id}
        )
        cls.cat_level3 = cat_obj.create(
            {"name": "Category Level 3", "parent_id": cls.cat_level2.id}
        )


class TestShopinvaderCategory(TestShopinvaderCategoryBase):
    def test_category(self):
        res = ProductCategory.from_product_category(self.cat_level3).model_dump()
        self.assertEqual(res["level"], 2)
        self.assertEqual(res["parent"]["name"], "Category Level 2")
        self.assertEqual(res["parent"]["parent"]["name"], "Category Level 1")

        res = ProductCategory.from_product_category(self.cat_level1).model_dump()
        self.assertEqual(res["level"], 0)
        self.assertEqual(len(res["childs"]), 1)
        self.assertEqual(res["childs"][0]["name"], "Category Level 2")
        self.assertEqual(res["childs"][0]["childs"][0]["name"], "Category Level 3")
