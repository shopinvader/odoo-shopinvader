# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from .common import CommonCase


class BackendCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(BackendCase, cls).setUpClass()
        cls.lang_fr = cls._install_lang(cls, "base.lang_fr")
        cls.env = cls.env(
            context=dict(cls.env.context, test_queue_job_no_delay=True)
        )
        cls.backend = cls.backend.with_context(test_queue_job_no_delay=True)

    def _all_products_count(self):
        return self.env["product.template"].search_count(
            [("sale_ok", "=", True)]
        )

    def _all_products_binding_count(self):
        return self.env["shopinvader.product"].search_count([])

    def _bind_all_product(self, domain=None):
        self.backend.bind_all_product(domain=domain)

    def _bind_all_category(self, domain=None):
        self.backend.bind_all_category(domain=domain)

    def test_bind_all_product(self):
        self.assertEqual(
            self._all_products_count(), self._all_products_binding_count()
        )

    @mute_logger("odoo.models.unlink")
    def test_rebind_all_product(self):
        self._bind_all_product()
        self.env["shopinvader.variant"].search([], limit=1).unlink()
        self.assertEqual(
            self._all_products_count(), self._all_products_binding_count()
        )

    def _setup_bind_all_products(self):
        """Generate isolated data to test product/category binding."""
        self.env["shopinvader.category"].search([]).unlink()
        self.env["shopinvader.variant"].search([]).unlink()
        self.env["shopinvader.product"].search([]).unlink()
        prod1 = self.env.ref(
            "shopinvader.product_template_armchair_mid_century"
        )
        prod2 = self.env.ref(
            "shopinvader.product_product_table_walmut"
        ).product_tmpl_id
        prod3 = self.env.ref("shopinvader.product_template_chair_mid_century")
        prod4 = self.env.ref(
            "shopinvader.product_product_chair_mid_century_red"
        ).product_tmpl_id
        # create our own categories w/ specific hierarchy to avoid
        # test data conflicts / regressions
        categ_model = self.env["product.category"]
        categ_lvl0 = categ_model.create({"name": "Root"})
        categ_lvl1 = categ_model.create(
            {"name": "Level 1", "parent_id": categ_lvl0.id}
        )
        categ_lvl2 = categ_model.create(
            {"name": "Level 2", "parent_id": categ_lvl1.id}
        )
        categ_lvl3 = categ_model.create(
            {"name": "Level 3", "parent_id": categ_lvl2.id}
        )
        categ_lvl4 = categ_model.create(
            {"name": "Level 4", "parent_id": categ_lvl3.id}
        )
        prod1.categ_id = categ_lvl1
        prod2.categ_id = categ_lvl2
        prod3.categ_id = categ_lvl3
        prod4.categ_id = categ_lvl4
        return {
            "all_prods": prod1 + prod2 + prod3 + prod4,
            "prod1": prod1,
            "prod2": prod2,
            "prod3": prod3,
            "prod4": prod4,
            "all_categs": categ_lvl0
            + categ_lvl1
            + categ_lvl2
            + categ_lvl3
            + categ_lvl4,
            "categ_lvl0": categ_lvl0,
            "categ_lvl1": categ_lvl1,
            "categ_lvl2": categ_lvl2,
            "categ_lvl3": categ_lvl3,
            "categ_lvl4": categ_lvl4,
        }

    @mute_logger("odoo.models.unlink")
    def test_bind_all_product_and_autobind_category(self):
        self.env["shopinvader.category"].search([]).unlink()
        self.backend.category_binding_level = 2
        records = self._setup_bind_all_products()
        self._bind_all_product([("id", "in", records["all_prods"].ids)])
        # count all categs because they are assigned directly to products
        expected = records["all_categs"]
        self.assertEqual(
            len(expected), self.env["shopinvader.category"].search_count([])
        )

    @mute_logger("odoo.models.unlink")
    def test_bind_all_product_and_autobind_category_root_level(self):
        self.backend.category_root_binding_level = 1
        self.backend.category_binding_level = 3
        records = self._setup_bind_all_products()
        self._bind_all_product([("id", "in", records["all_prods"].ids)])
        # categ_lvl4 is included because attached directly to the product
        expected = records["all_categs"] - records["categ_lvl0"]
        self.assertEqual(
            len(expected), self.env["shopinvader.category"].search_count([])
        )
        # remove another level
        self.backend.category_root_binding_level = 2
        self.env["shopinvader.category"].search([]).unlink()
        self._bind_all_product([("id", "in", records["all_prods"].ids)])
        expected = (
            records["categ_lvl2"]
            + records["categ_lvl3"]
            + records["categ_lvl4"]
        )
        self.assertEqual(
            len(expected), self.env["shopinvader.category"].search_count([])
        )

    def test_bind_all_category(self):
        self._bind_all_category()
        self.assertEqual(
            self.env["product.category"].search_count([]),
            self.env["shopinvader.category"].search_count([]),
        )

    @mute_logger("odoo.models.unlink")
    def test_rebind_all_category(self):
        self._bind_all_category()
        self.env["shopinvader.category"].search([], limit=1).unlink()
        self._bind_all_category()
        self.assertEqual(
            self.env["product.category"].search_count([]),
            self.env["shopinvader.category"].search_count([]),
        )

    def test_add_new_lang_rebind(self):
        """
        Data:
            * A backend with 1 lang and all products binded for this lang
        Test Case:
            * Add a new lang
        Expected result:
            * A binding exits for each binded products in each lang
        """
        self._bind_all_product()
        self._bind_all_category()
        binded_variants_count = self.env["shopinvader.variant"].search_count(
            []
        )
        binded_categories_count = self.env[
            "shopinvader.category"
        ].search_count([])
        self.backend.write({"lang_ids": [(4, self.lang_fr.id)]})
        self.assertEqual(
            self.env["shopinvader.variant"].search_count([]),
            binded_variants_count * 2,
        )
        self.assertEqual(
            self.env["shopinvader.category"].search_count([]),
            binded_categories_count * 2,
        )

    def test_remove_lang_rebind(self):
        """
        Data:
            * A backend with 1 lang and all products binded for this lang
        Test Case:
            * Remove lang
        Expected result:
            * No binding exists
        """
        self._bind_all_product()
        self._bind_all_category()
        self.backend.write({"lang_ids": [(5, None, None)]})
        self.assertEqual(self.env["shopinvader.variant"].search_count([]), 0)
        self.assertEqual(self.env["shopinvader.category"].search_count([]), 0)
