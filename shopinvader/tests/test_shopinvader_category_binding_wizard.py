# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .test_shopinvader_category import TestShopinvaderCategoryBase


class TestShopinvaderCategoryBindingWizard(TestShopinvaderCategoryBase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderCategoryBindingWizard, cls).setUpClass()
        cls.bind_wizard_model = cls.env["shopinvader.category.binding.wizard"]
        cls.unbind_wizard_model = cls.env[
            "shopinvader.category.unbinding.wizard"
        ]

    def test_category_binding(self):
        """
        Select a category and
        - bind it to a shopinvader backend
        - unbind it
        - bind it again
        """
        category_bind_model = self.category_bind_model
        unbind_wizard_model = self.unbind_wizard_model
        bind_wizard_model = self.bind_wizard_model
        product_category = self.product_category
        backend = self.backend
        self.assertFalse(product_category.shopinvader_bind_ids)

        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_category_ids": [(6, 0, product_category.ids)],
            }
        )

        bind_wizard.action_bind_categories()
        domain = [
            ("record_id", "=", product_category.id),
            ("backend_id", "=", backend.id),
        ]

        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        self.assertEqual(len(bind_record), 1)
        self.assertEqual(bind_record, product_category.shopinvader_bind_ids)

        # Do the same for the second backend
        bind_wizard2 = self.bind_wizard_model.create(
            {
                "backend_id": self.backend2.id,
                "product_category_ids": [(6, 0, product_category.ids)],
            }
        )

        bind_wizard2.action_bind_categories()
        domain_bk2 = [
            ("record_id", "=", product_category.id),
            ("backend_id", "=", self.backend2.id),
        ]

        # A binding record should exists
        bind_record_bk2 = category_bind_model.search(domain_bk2)
        self.assertEqual(len(bind_record_bk2), 1)
        self.assertIn(bind_record_bk2, product_category.shopinvader_bind_ids)

        # --------------------------------
        # UnBind the category
        # --------------------------------
        unbind_wizard = unbind_wizard_model.create(
            {"shopinvader_category_ids": [(6, 0, bind_record.ids)]}
        )
        unbind_wizard.action_unbind_categories()

        # The binding record should be unreachable
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 0)
        # Still exists
        self.assertTrue(bind_record_bk2.exists())

        # The binding record should still exist but inactive
        bind_record = category_bind_model.with_context(
            active_test=False
        ).search(domain)

        self.assertEqual(len(bind_record), 1)

        # --------------------------------
        # Bind the category again
        # --------------------------------
        values = {
            "backend_id": backend.id,
            "product_category_ids": [(6, 0, product_category.ids)],
        }
        # Active test because product.category is active = False
        bind_wizard = bind_wizard_model.create(values)
        bind_wizard.action_bind_categories()

        # The binding record should be re-activated
        bind_record = self.category_bind_model.search(domain)
        self.assertEqual(len(bind_record), 1)

    def test_category_binding_multi_lang(self):
        """
        With more than 1 lang, select a category and
        - bind it to a shopinvader backend
        - unbind it
        - bind it again
        """
        lang = self._install_lang("base.lang_fr")
        self.backend.lang_ids |= lang
        self.backend2.lang_ids |= lang
        category_bind_model = self.category_bind_model
        unbind_wizard_model = self.unbind_wizard_model
        bind_wizard_model = self.bind_wizard_model
        product_category = self.product_category
        backend = self.backend
        self.assertFalse(product_category.shopinvader_bind_ids)

        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_category_ids": [(6, 0, product_category.ids)],
            }
        )
        bind_wizard.action_bind_categories()
        domain = [
            ("record_id", "=", product_category.id),
            ("backend_id", "=", backend.id),
        ]

        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        # 2 (because 2 languages installed)
        self.assertEqual(len(bind_record), 2)
        self.assertEqual(bind_record, product_category.shopinvader_bind_ids)

        # Do the same for the second backend
        bind_wizard2 = self.bind_wizard_model.create(
            {
                "backend_id": self.backend2.id,
                "product_category_ids": [(6, 0, product_category.ids)],
            }
        )
        bind_wizard2.action_bind_categories()
        domain_bk2 = [
            ("record_id", "=", product_category.id),
            ("backend_id", "=", self.backend2.id),
        ]

        # A binding record should exists
        bind_record_bk2 = category_bind_model.search(domain_bk2)
        # 2 (because 2 languages installed)
        self.assertEqual(len(bind_record_bk2), 2)
        for shopinv_categ in bind_record_bk2:
            self.assertIn(shopinv_categ, product_category.shopinvader_bind_ids)

        # --------------------------------
        # UnBind the category
        # --------------------------------
        unbind_wizard = unbind_wizard_model.create(
            {"shopinvader_category_ids": [(6, 0, bind_record.ids)]}
        )
        unbind_wizard.action_unbind_categories()

        # The binding record should be unreachable
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 0)
        for shopinv_categ in bind_record_bk2:
            # Still exists
            self.assertTrue(shopinv_categ.exists())
        # The binding record should still exist but inactive
        bind_record = category_bind_model.with_context(
            active_test=False
        ).search(domain)

        self.assertEqual(len(bind_record), 2)

        # --------------------------------
        # Bind the category again
        # --------------------------------
        values = {
            "backend_id": backend.id,
            "product_category_ids": [(6, 0, product_category.ids)],
        }
        # Active test because product.category is active = False
        bind_wizard = bind_wizard_model.create(values)
        bind_wizard.action_bind_categories()

        # The binding record should be re-activated
        bind_record = self.category_bind_model.search(domain)
        self.assertEqual(len(bind_record), 2)

    def test_category_inactivation(self):
        """
        Select a category and bind it to a Lengow Catalogue
        Inactivation of the category must unbind the category
        """
        bind_wizard_model = self.bind_wizard_model
        category_bind_model = self.category_bind_model
        product_category = self.product_category
        backend = self.backend
        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_category_ids": [(6, 0, product_category.ids)],
            }
        )
        bind_wizard.action_bind_categories()

        domain = [
            ("record_id", "=", product_category.id),
            ("backend_id", "=", backend.id),
        ]
        # A binding record should exists
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 1)

        # --------------------------------
        # Inactivate the category
        # --------------------------------
        product_category.write({"active": False})

        # The binding record should be unreachable
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 0)

        # --------------------------------
        # Re-activate the category
        # --------------------------------
        product_category.write({"active": True})

        # The binding record should be still unreachable
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 0)
        bind_wizard.action_bind_categories()
        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        self.assertTrue(bind_record)
        # Disable the category and the binded record should be disabled too
        product_category.write({"active": False})
        self.assertFalse(bind_record.active)

    def test_child_no_auto_bind(self):
        bind_wizard_model = self.bind_wizard_model
        category_bind_model = self.category_bind_model
        backend = self.backend

        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "product_category_ids": [(6, 0, self.cat_level1.ids)],
            }
        )
        bind_wizard.action_bind_categories()

        domain = [
            (
                "record_id",
                "in",
                [self.cat_level1.id, self.cat_level2.id, self.cat_level3.id],
            ),
            ("backend_id", "=", backend.id),
        ]

        # A binding record should exists
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 1)

    def test_child_auto_bind(self):
        unbind_wizard_model = self.unbind_wizard_model
        bind_wizard_model = self.bind_wizard_model
        category_bind_model = self.category_bind_model
        backend = self.backend

        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": backend.id,
                "child_autobinding": True,
                "product_category_ids": [(6, 0, self.cat_level1.ids)],
            }
        )
        bind_wizard.action_bind_categories()

        domain = [
            (
                "record_id",
                "in",
                [self.cat_level1.id, self.cat_level2.id, self.cat_level3.id],
            ),
            ("backend_id", "=", backend.id),
        ]

        # A binding record should exists
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 3)

        # --------------------------------
        # UnBind the category
        # --------------------------------
        parent_level = bind_record.filtered(
            lambda x: x.record_id.id == self.cat_level1.id
        )
        unbind_wizard = unbind_wizard_model.create(
            {"shopinvader_category_ids": [(6, 0, parent_level.ids)]}
        )
        unbind_wizard.action_unbind_categories()

        # The binding record should be unreachable
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 0)
