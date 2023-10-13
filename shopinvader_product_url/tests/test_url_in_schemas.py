# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductCategory, ProductProduct


class TestUrlInSchemas(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()

        cls.parent_category = cls.env["product.category"].create(
            {
                "name": "test parent category",
            }
        )
        cls.child_category = cls.env["product.category"].create(
            {
                "name": "test child category",
                "parent_id": cls.parent_category.id,
            }
        )
        cls.child_child_category = cls.env["product.category"].create(
            {
                "name": "test child child category",
                "parent_id": cls.child_category.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "categ_id": cls.child_child_category.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.reset_extendable_registry()
        super().tearDownClass()

    def test_product_product(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.url_key, "test-product")
        self.assertEqual(product.redirect_url_key, [])
        # if we update the product name, the url_key should be updated
        # and a redirect_url_key should be created
        self.product.name = "new test product"
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.url_key, "new-test-product")
        self.assertEqual(product.redirect_url_key, ["test-product"])
        # we should have 3 categories on the product ordered by level
        # with the url_key of the category
        self.assertEqual(len(product.categories), 3)
        self.assertEqual(product.categories[0].url_key, "test-parent-category")
        self.assertEqual(
            product.categories[1].url_key,
            "test-parent-category/test-child-category",
        )
        self.assertEqual(
            product.categories[2].url_key,
            "test-parent-category/test-child-category/test-child-child-category",
        )

    def test_product_category(self):
        category = ProductCategory.from_product_category(self.child_child_category)
        self.assertEqual(
            category.url_key,
            "test-parent-category/test-child-category/test-child-child-category",
        )
        self.assertEqual(category.redirect_url_key, [])
        # if we update the category name, the url_key should be updated whatever the level
        # and a redirect_url_key should be created
        self.parent_category.name = "parent"
        category = ProductCategory.from_product_category(self.child_child_category)
        self.assertEqual(
            category.url_key,
            "parent/test-child-category/test-child-child-category",
        )
        self.assertEqual(
            category.redirect_url_key,
            ["test-parent-category/test-child-category/test-child-child-category"],
        )
