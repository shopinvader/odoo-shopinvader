# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
from odoo.addons.component.tests.common import SavepointComponentCase

from .common import CommonMixin


class TestShopinvaderCategoryBase(SavepointComponentCase, CommonMixin):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderCategoryBase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend2 = cls.env.ref("shopinvader.backend_2")
        cls.product_category = cls.env.ref("product.product_category_4")
        cls.category_bind_model = cls.env["shopinvader.category"]
        cat_obj = cls.env["product.category"]

        cls.cat_level1 = cat_obj.create({"name": "Category Level 1"})
        cls.cat_level2 = cat_obj.create(
            {"name": "Category Level 2", "parent_id": cls.cat_level1.id}
        )
        cls.cat_level3 = cat_obj.create(
            {"name": "Category Level 3", "parent_id": cls.cat_level2.id}
        )
        cls.cat_level1._parent_store_compute()


class TestShopinvaderCategory(TestShopinvaderCategoryBase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderCategory, cls).setUpClass()
        cls.binding_l1 = cls._create_binding(cls.cat_level1)
        cls.binding_l2 = cls._create_binding(cls.cat_level2)
        cls.binding_l3 = cls._create_binding(cls.cat_level3)

    @classmethod
    def _create_binding(cls, product_category, **kw):
        vals = {
            "backend_id": cls.backend.id,
            "record_id": product_category.id,
            "lang_id": cls.env.ref("base.lang_en").id,
        }
        vals.update(kw)
        return cls.category_bind_model.create(vals)

    def test_category_url(self):
        self.assertEqual(self.binding_l1.url_key, "category-level-1")
        self.assertEqual(
            self.binding_l2.url_key, "category-level-1/category-level-2"
        )
        self.assertEqual(
            self.binding_l3.url_key,
            "category-level-1/category-level-2/category-level-3",
        )

    def test_category_url_inactive_parent(self):
        self.binding_l1.active = False
        self.assertEqual(self.binding_l2.url_key, "category-level-2")
        self.assertEqual(
            self.binding_l3.url_key, "category-level-2/category-level-3"
        )
        self.binding_l2.active = False
        self.assertEqual(self.binding_l3.url_key, "category-level-3")

    def test_redirect_category_url(self):
        self.assertEqual(self.binding_l1.url_key, "category-level-1")
        self.binding_l1.record_id.name = "category level 1 renamed"
        self.assertEqual(self.binding_l1.url_key, "category-level-1-renamed")
        self.assertEqual(
            self.binding_l1.redirect_url_key, ["category-level-1"]
        )
