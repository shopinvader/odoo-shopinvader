# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from uuid import uuid4

from odoo import fields
from odoo.tools import mute_logger

from .common import ProductCommonCase


class ProductCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.backend = cls.backend.with_context(test_queue_job_no_delay=True)

    def test_create_shopinvader_variant(self):
        self.assertEqual(
            len(self.template.product_variant_ids),
            len(self.shopinvader_variants),
        )

    # TODO MIGRATE
    #    def test_categories(self):
    #        self.assertEqual(
    #            len(self.shopinvader_variant.shopinvader_categ_ids), 0)
    #        self.backend.bind_all_category()
    #        self.shopinvader_variant.invalidate_cache()
    #        self.assertEqual(
    #            len(self.shopinvader_variant.shopinvader_categ_ids), 2)
    #        self.assertEqual(
    #            self.shopinvader_variant.shopinvader_categ_ids.mapped('record_id'),
    #            self.template.categ_id + self.template.categ_id.parent_id)
    #
    def test_variant_attributes(self):
        attr_dict = {"legs": u"Steel", "color": u"Black"}
        self.assertDictEqual(self.shopinvader_variant.variant_attributes, attr_dict)

    def test_product_price(self):
        self.assertEqual(
            self.shopinvader_variant.price,
            {
                "default": {
                    "discount": 0.0,
                    "original_value": 750.0,
                    "tax_included": True,
                    "value": 750.0,
                }
            },
        )

    @contextmanager
    def _check_url(self, shopinvader_variants):
        """
        Check url if name has been updated
        :param shopinvader_variants: shopinvader.variant recordset
        :return:
        """
        shopinv_variant_names = {r: r.name for r in shopinvader_variants}
        shopinv_variant_urls = {r: r.url_url_ids for r in shopinvader_variants}
        yield
        shopinvader_variants.refresh()
        for shopinv_variant in shopinvader_variants:
            existing_urls = shopinv_variant_urls.get(shopinv_variant)
            new_url = shopinv_variant.url_url_ids.filtered(
                lambda u: u not in existing_urls
            )
            if shopinv_variant_names.get(shopinv_variant) != shopinv_variant.name:
                self.assertEqual(len(new_url), 1)
            else:
                self.assertEqual(len(new_url), 0)

    def test_product_name_url(self):
        """
        Check the case where the product template has a new name.
        Do the write directly on the product template to check if a new url
        is automatically created (as the inherit from abstract url is done
        on shopinvader.product and not on product.template).
        :return:
        """
        product_product = self.shopinvader_variant.record_id
        # The name updated
        with self._check_url(self.shopinvader_variant):
            product_product.write({"name": str(uuid4())})
        # The name is not really updated
        with self._check_url(self.shopinvader_variant):
            product_product.write({"name": product_product.name})
        return

    def test_product_get_price(self):
        # self.base_pricelist doesn't define a tax mapping. We are tax included
        fiscal_position_fr = self.env.ref("shopinvader.fiscal_position_0")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=fiscal_position_fr
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 750.0,
                "tax_included": True,
                "value": 750.0,
            },
        )
        # promotion price list define a discount of 20% on all product
        promotion_price_list = self.env.ref("shopinvader.pricelist_1")
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=fiscal_position_fr
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 600.0,
                "tax_included": True,
                "value": 600.0,
            },
        )
        # use a fiscal position defining a mapping from tax included to tax
        # excluded
        tax_exclude_fiscal_position = self.env.ref("shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=tax_exclude_fiscal_position
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 652.17,
                "tax_included": False,
                "value": 652.17,
            },
        )
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=tax_exclude_fiscal_position
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 521.74,
                "tax_included": False,
                "value": 521.74,
            },
        )

    def test_product_get_price_zero(self):
        # Test that discount calculation does not fail if original price is 0
        self.shopinvader_variant.list_price = 0
        self.base_pricelist.discount_policy = "without_discount"
        self.env["product.pricelist.item"].create(
            {
                "product_id": self.shopinvader_variant.record_id.id,
                "pricelist_id": self.base_pricelist.id,
                "fixed_price": 10,
            }
        )
        fiscal_position_fr = self.env.ref("shopinvader.fiscal_position_0")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=fiscal_position_fr
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 0.0,
                "tax_included": True,
                "value": 10.0,
            },
        )

    def test_product_get_price_per_qty(self):
        # Define a promotion price for the product with min_qty = 10
        fposition = self.env.ref("shopinvader.fiscal_position_0")
        pricelist = self.base_pricelist
        self.env["product.pricelist.item"].create(
            {
                "name": "Discount on Product when Qty >= 10",
                "pricelist_id": pricelist.id,
                "base": "list_price",
                "compute_price": "percentage",
                "percent_price": "20",
                "applied_on": "0_product_variant",
                "product_id": self.shopinvader_variant.record_id.id,
                "min_quantity": 10.0,
            }
        )
        # Case 1 (qty = 1.0). No discount is applied
        price = self.shopinvader_variant._get_price(
            qty=1.0, pricelist=pricelist, fposition=fposition
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 750.0,
                "tax_included": True,
                "value": 750.0,
            },
        )
        # Case 2 (qty = 10.0). Discount is applied
        # promotion price list define a discount of 20% on all product
        price = self.shopinvader_variant._get_price(
            qty=10.0, pricelist=pricelist, fposition=fposition
        )
        self.assertDictEqual(
            price,
            {
                "discount": 0.0,
                "original_value": 600.0,
                "tax_included": True,
                "value": 600.0,
            },
        )

    def test_product_get_price_discount_policy(self):
        # Ensure that discount is with 2 digits
        self.env.ref("product.decimal_discount").digits = 2
        # self.base_pricelist doesn't define a tax mapping. We are tax included
        # we modify the discount_policy
        self.base_pricelist.discount_policy = "without_discount"
        fiscal_position_fr = self.env.ref("shopinvader.fiscal_position_0")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=fiscal_position_fr
        )
        self.assertDictEqual(
            price,
            {
                "tax_included": True,
                "value": 750.0,
                "discount": 0.0,
                "original_value": 750.0,
            },
        )
        # promotion price list define a discount of 20% on all product
        # we modify the discount_policy
        promotion_price_list = self.env.ref("shopinvader.pricelist_1")
        promotion_price_list.discount_policy = "without_discount"
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=fiscal_position_fr
        )
        self.assertDictEqual(
            price,
            {
                "tax_included": True,
                "value": 600.0,
                "discount": 20.0,
                "original_value": 750.0,
            },
        )
        # use the fiscal position defining a mapping from tax included to tax
        # excluded
        # Tax mapping should not impact the computation of the discount and
        # the original value
        tax_exclude_fiscal_position = self.env.ref("shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=tax_exclude_fiscal_position
        )
        self.assertDictEqual(
            price,
            {
                "tax_included": False,
                "value": 652.17,
                "discount": 0.0,
                "original_value": 652.17,
            },
        )
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=tax_exclude_fiscal_position
        )
        self.assertDictEqual(
            price,
            {
                "tax_included": False,
                "value": 521.74,
                "discount": 20.0,
                "original_value": 652.17,
            },
        )

    def test_category_child_with_one_lang(self):
        """
        Main category children should equal shopinvader children
        """
        self.backend.bind_all_category()
        categ = self.env.ref("product.product_category_1")
        # Use this to compare, as the amount can vary depending
        # on base modules installed
        children = categ.child_id
        shopinvader_categ = categ.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_categ), 1)
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), len(children))

    def test_category_child_with_two_lang(self):
        lang = self._install_lang("base.lang_fr")
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        categ = self.env.ref("product.product_category_1")
        # Use this to compare, as the amount can vary depending
        # on base modules installed
        children = categ.child_id
        categ.with_context(lang="fr_FR").write({"name": "En Vente"})
        categ.parent_id.with_context(lang="fr_FR").write({"name": "Tous"})
        self.assertEqual(len(categ.shopinvader_bind_ids), 2)
        shopinvader_categ = categ.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), len(children))
        for binding in categ.shopinvader_bind_ids:
            self.assertEqual(binding.shopinvader_parent_id.lang_id, binding.lang_id)
            if binding.lang_id.code == "fr_FR":
                self.assertEqual(binding.url_key, u"tous/en-vente")
            elif binding.lang_id.code == "en_US":
                self.assertEqual(binding.url_key, u"all/saleable")

    def test_product_category_with_one_lang(self):
        self.backend.bind_all_category()
        product = self.env.ref("product.product_product_4")
        self.assertEqual(len(product.shopinvader_bind_ids), 1)
        shopinvader_product = product.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)

    def test_product_category_with_two_lang(self):
        lang = self._install_lang("base.lang_fr")
        product = self.env.ref("product.product_product_4")
        product.with_context(lang="fr_FR").name = "Bureau Personnalisable"
        product.flush()
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        self.backend.bind_all_product()
        self.assertEqual(len(product.shopinvader_bind_ids), 2)
        shopinvader_product = product.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)
        for binding in product.shopinvader_bind_ids:
            if binding.lang_id.code == "fr_FR":
                self.assertEqual(binding.url_key, u"bureau-personnalisable")
            elif binding.lang_id.code == "en_US":
                self.assertEqual(binding.url_key, u"customizable-desk-config")

    def test_create_product_binding1(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template not published (so no
        shopinvader.variant should be created)
        :return: bool
        """
        product_tmpl_obj = self.env["product.template"].with_context(active_test=False)
        product_values = {"name": "Shopinvader t-shirt"}
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertFalse(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertFalse(product_product.shopinvader_bind_ids)
        return True

    def test_create_product_binding2(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is not published
        (but with a shopinvader.product related) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        product_tmpl_obj = self.env["product.template"].with_context(active_test=False)
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        product_values = {
            "name": "Shopinvader t-shirt",
            "shopinvader_bind_ids": [
                (
                    0,
                    False,
                    {
                        "backend_id": backend.id,
                        "lang_id": lang.id,
                        "active": False,
                    },
                )
            ],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        return True

    def test_create_product_binding3(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is published
        (with a shopinvader.product related and active = True) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        product_tmpl_obj = self.env["product.template"].with_context(active_test=False)
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        product_values = {
            "name": "Shopinvader t-shirt",
            "shopinvader_bind_ids": [
                (
                    0,
                    False,
                    {
                        "backend_id": backend.id,
                        "lang_id": lang.id,
                        "active": True,
                    },
                )
            ],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        return True

    @mute_logger("odoo.models.unlink")
    def test_create_product_binding4(self):
        """
        Test the creation of a product.template.
        During the creation of a new product.template, Odoo create
        automatically a new product.product.
        If the product.template doesn't have a shopinvader.product, we should
        create a new shopinvader.variant (because the product is not published)
        But if it's published, we should create a shopinvader.variant for each
        product.product related to this product.template.
        So each time a product.product is created, we should check if we need
        to create a shopinvader.variant.
        For this test, we create a product.template who is published
        (with a shopinvader.product related and active = True) so the related
        product.product should have a shopinvader.variant.
        :return: bool
        """
        backend = self.backend
        color_attribute = self.env.ref("product.product_attribute_2")
        white_attr = self.env.ref("product.product_attribute_value_3")
        black_attr = self.env.ref("product.product_attribute_value_4")
        attr = white_attr | black_attr
        product_tmpl_obj = self.env["product.template"].with_context(active_test=False)
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        product_values = {
            "name": "Shopinvader t-shirt",
            "shopinvader_bind_ids": [
                (
                    0,
                    False,
                    {
                        "backend_id": backend.id,
                        "lang_id": lang.id,
                        "active": True,
                    },
                )
            ],
        }
        product_tmpl = product_tmpl_obj.create(product_values)
        self.assertTrue(product_tmpl.shopinvader_bind_ids)
        product_product = product_tmpl.product_variant_ids
        self.assertEqual(len(product_product.shopinvader_bind_ids), 1)
        self.assertFalse(product_product.shopinvader_bind_ids.active)
        # Then we add some products attributes (to create some variants)
        product_tmpl.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": color_attribute.id,
                            "value_ids": [(6, False, attr.ids)],
                        },
                    )
                ]
            }
        )
        self.assertEqual(len(attr), len(product_tmpl.product_variant_ids))
        self.assertEqual(
            len(attr),
            len(product_tmpl.shopinvader_bind_ids.shopinvader_variant_ids),
        )
        return True

    def test_editing_product_with_sale_manager_user(self):
        # test that product can still be edited without issue
        # when automatically generating a new url
        self.user = self.env.ref("base.user_demo")
        self.user.write(
            {
                "groups_id": [
                    (4, self.env.ref("sales_team.group_sale_manager").id),
                    (
                        4,
                        self.env.ref("shopinvader.group_shopinvader_manager").id,
                    ),
                ]
            }
        )
        self.env = self.env(user=self.user)
        product = self.env["product.template"].search(
            [("shopinvader_bind_ids", "!=", False)], limit=1
        )
        product.name += " modification"

    def test_multicompany_product(self):
        # Test that default code change with user on company 2
        # changes the url_key on company 1 backend
        product_12 = self.env.ref("product.product_product_12")
        shopinvader_product_12 = self.env["shopinvader.product"].search(
            [
                ("record_id", "=", product_12.product_tmpl_id.id),
                ("backend_id", "=", self.backend.id),
            ]
        )
        result = shopinvader_product_12.url_key.find(product_12.default_code)
        self.assertTrue(result)
        # If sale_stock module have been installed
        # We need to drop the constraint as at that moment the module
        # is not loaded (shopinvader do not depend on it)
        sale_stock = self.env["ir.module.module"].search([("name", "=", "sale_stock")])
        if sale_stock.state == "installed":
            self.cr.execute(
                """ALTER TABLE res_company
                ALTER COLUMN security_lead
                DROP NOT NULL"""
            )
        # Now we can create the company
        company_2 = self.env["res.company"].create(
            {"name": "Company2", "currency_id": self.env.ref("base.EUR").id}
        )
        # Set product shareable between companies
        product_12.company_id = False
        # Change product name to trigger compute
        product_12.write(
            {
                "name": "Wireless Mouse MultiCompany",
                "default_code": "product_12_mc",
            }
        )
        result = shopinvader_product_12.with_context(
            allowed_company_ids=[company_2.id]
        ).url_key.find("product_12_mc")
        self.assertTrue(result)

    def test_product_shopinvader_name(self):
        product = self.shopinvader_variant.shopinvader_product_id
        product.shopinvader_name = "Test shopinvader name"
        self.assertEqual(product.shopinvader_display_name, product.name)
        self.backend.use_shopinvader_product_name = True
        self.assertEqual(product.shopinvader_display_name, product.shopinvader_name)

    def _check_category_level(self, shopinv_categs):
        """
        Check if category level of given shopinvader categories
        :param shopinv_categs: shopinvader.category recordset
        :return: bool
        """
        for shopinv_categ in shopinv_categs:
            level = 0
            parent = shopinv_categ.shopinvader_parent_id
            while parent and parent.active:
                level += 1
                parent = parent.shopinvader_parent_id
            self.assertEqual(shopinv_categ.level, level)
        return True

    def test_product_category_auto_bind(self):
        """
        Test if after a product binding, the category is automatically binded
        too (depending on the configuration).
        :return:
        """
        product = self.env.ref("product.product_product_4").copy()
        # To avoid others products to be binded
        self.env["product.template"].search(
            [("sale_ok", "=", True), ("id", "not in", product.ids)]
        ).write({"sale_ok": False})
        product.write({"sale_ok": True})
        categ_obj = self.env["product.category"]
        shopinv_categ_obj = self.env["shopinvader.category"]
        existing_binded_categs = shopinv_categ_obj.search([])
        categ_grand_parent = categ_obj.create({"name": "Cool grand-parent"})
        categ_parent = categ_obj.create(
            {"name": "Strict parent", "parent_id": categ_grand_parent.id}
        )
        categ_child = categ_obj.create(
            {"name": "normal child", "parent_id": categ_parent.id}
        )
        categs = categ_grand_parent | categ_parent | categ_child
        product.write({"categ_id": categ_child.id})
        # New categories shouldn't be binded yet
        self.assertFalse(shopinv_categ_obj.search([("record_id", "in", categs.ids)]))
        self.backend.write({"category_binding_level": 0})
        self.backend.bind_all_product()
        self.assertEqual(existing_binded_categs, shopinv_categ_obj.search([]))
        # New categories shouldn't be binded due to binded level set to 0
        self.assertFalse(shopinv_categ_obj.search([("record_id", "in", categs.ids)]))
        self.backend.write({"category_binding_level": 2})
        self.backend.bind_all_product()
        categ_level2 = categ_child
        categ_level2 |= categ_child.mapped("parent_id")
        shopinv_products = self.env["shopinvader.variant"].search(
            [("backend_id", "=", self.backend.id)]
        )
        categs_binded = shopinv_products.mapped("categ_id")
        categs_binded |= categs_binded.mapped("parent_id")
        existing_binded_categs |= shopinv_categ_obj.search(
            [("record_id", "in", categs_binded.ids)]
        )
        self._check_category_level(existing_binded_categs)
        # Ensure no others categories are binded
        self.assertEqual(existing_binded_categs, shopinv_categ_obj.search([]))
        # categ_child and categ_parent should be binded but not the categ
        # grand_parent due to binding_level defined on 2
        binded_categs = shopinv_categ_obj.search(
            [("record_id", "in", categs.ids)]
        ).mapped("record_id")
        self.assertIn(categ_parent, binded_categs)
        self.assertIn(categ_child, binded_categs)
        self.assertNotIn(categ_grand_parent, binded_categs)

    def test_product_category_auto_bind_wizard(self):
        """
        Test if after a product binding, the category is automatically binded
        too (depending on the configuration) using the wizard.
        :return:
        """
        wizard_obj = self.env["shopinvader.variant.binding.wizard"]
        product = self.env.ref("product.product_product_4").copy()
        wizard_values = {
            "backend_id": self.backend.id,
            "product_ids": [(6, False, product.ids)],
        }
        categ_obj = self.env["product.category"]
        shopinv_categ_obj = self.env["shopinvader.category"]
        existing_binded_categs = shopinv_categ_obj.search([])
        categ_grand_parent = categ_obj.create({"name": "Cool grand-parent"})
        categ_parent = categ_obj.create(
            {"name": "Strict parent", "parent_id": categ_grand_parent.id}
        )
        categ_child = categ_obj.create(
            {"name": "normal child", "parent_id": categ_parent.id}
        )
        categs = categ_grand_parent | categ_parent | categ_child
        product.write({"categ_id": categ_child.id})
        wizard = wizard_obj.create(wizard_values)
        # New categories shouldn't be binded yet
        self.assertFalse(shopinv_categ_obj.search([("record_id", "in", categs.ids)]))
        self.backend.write({"category_binding_level": 0})
        wizard.bind_products()
        self.assertEqual(existing_binded_categs, shopinv_categ_obj.search([]))
        # New categories shouldn't be binded due to binded level set to 0
        self.assertFalse(shopinv_categ_obj.search([("record_id", "in", categs.ids)]))
        self.backend.write({"category_binding_level": 2})
        wizard.bind_products()
        shopinv_products = self.env["shopinvader.variant"].search(
            [("backend_id", "=", self.backend.id)]
        )
        categs_binded = shopinv_products.mapped("categ_id")
        categs_binded |= categs_binded.mapped("parent_id")
        existing_binded_categs |= shopinv_categ_obj.search(
            [("record_id", "in", categs_binded.ids)]
        )
        self._check_category_level(existing_binded_categs)
        # Ensure no others categories are binded
        self.assertEqual(existing_binded_categs, shopinv_categ_obj.search([]))
        # categ_child and categ_parent should be binded but not the categ
        # grand_parent due to binding_level defined on 2
        binded_categs = shopinv_categ_obj.search(
            [("record_id", "in", categs.ids)]
        ).mapped("record_id")
        self.assertIn(categ_parent, binded_categs)
        self.assertIn(categ_child, binded_categs)
        self.assertNotIn(categ_grand_parent, binded_categs)

    def test_product_url1(self):
        """
        Test the little workflow about shopinvader variants and related URL.
        Expected behaviour:
        - On the unbind (active = False) => URL should be a redirect to a
        category who doesn't have children
        - On the bind (active = True) => Existing redirect URL should be
        deleted and new one should be re-generated
        For this case, we test a normal workflow: url should be related to
        the category (during unbind) and then we re-bind this product
        and new url should be generated
        :return:
        """
        bind_variant_model = self.env["shopinvader.variant.binding.wizard"]
        bind_category_model = self.env["shopinvader.category.binding.wizard"]
        product_tmpl_obj = self.env["product.template"]
        categ = self.env.ref("product.product_category_all")
        categ_wizard = bind_category_model.create(
            {
                "backend_id": self.backend.id,
                "product_category_ids": [(6, 0, categ.ids)],
            }
        )
        categ_wizard.action_bind_categories()
        domain = [
            ("record_id", "=", categ.id),
            ("backend_id", "=", self.backend.id),
        ]
        bind_categ = self.env["shopinvader.category"].search(domain)

        # For this case, the category should have children
        if bind_categ.shopinvader_child_ids:
            bind_categ.shopinvader_child_ids.unlink()
        product_values = {"name": "Shopinvader Rocket", "categ_id": categ.id}
        product_tmpl = product_tmpl_obj.create(product_values)
        product_product = product_tmpl.product_variant_ids

        product_wizard = bind_variant_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, product_product.ids)],
            }
        )
        product_wizard.bind_products()
        bind_product = self.env["shopinvader.product"].search(
            [
                ("record_id", "=", product_tmpl.id),
                ("backend_id", "=", self.backend.id),
            ]
        )
        self.assertIn(bind_categ, bind_product.shopinvader_categ_ids)
        urls = bind_product.url_url_ids
        self.assertEqual(urls.model_id, bind_product)
        bind_product.write({"active": False})

        bind_product.flush()
        self.assertEqual(urls.model_id, bind_categ)
        bind_product.write({"active": True})

        bind_product.flush()
        self.assertEqual(urls.model_id, bind_product)

    def test_product_url2(self):
        """
        Test the little workflow about shopinvader variants and related URL.
        Expected behaviour:
        - On the unbind (active = False) => URL should be a redirect to a
        category who doesn't have children
        - On the bind (active = True) => Existing redirect URL should be
        deleted and new one should be re-generated
        For this case, we simulate a normal workflow with different categories
        :return:
        """
        bind_variant_model = self.env["shopinvader.variant.binding.wizard"]
        bind_category_model = self.env["shopinvader.category.binding.wizard"]
        product_tmpl_obj = self.env["product.template"]
        categ_all = self.env.ref("product.product_category_all")
        categ2 = self.env.ref("product.product_category_2")
        categs = categ_all | categ2
        categ_wizard = bind_category_model.create(
            {
                "backend_id": self.backend.id,
                "product_category_ids": [(6, 0, categs.ids)],
            }
        )
        categ_wizard.action_bind_categories()
        domain = [
            ("record_id", "=", categ_all.id),
            ("backend_id", "=", self.backend.id),
        ]
        bind_categ_all = self.env["shopinvader.category"].search(domain)
        domain = [
            ("record_id", "=", categ2.id),
            ("backend_id", "=", self.backend.id),
        ]
        bind_categ2 = self.env["shopinvader.category"].search(domain)
        product_values = {"name": "Shopinvader Rocket", "categ_id": categ2.id}
        product_tmpl = product_tmpl_obj.create(product_values)
        product_product = product_tmpl.product_variant_ids

        product_wizard = bind_variant_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, product_product.ids)],
            }
        )
        product_wizard.bind_products()
        bind_product = self.env["shopinvader.product"].search(
            [
                ("record_id", "=", product_tmpl.id),
                ("backend_id", "=", self.backend.id),
            ]
        )
        self.assertIn(bind_categ_all, bind_product.shopinvader_categ_ids)
        self.assertIn(bind_categ2, bind_product.shopinvader_categ_ids)
        urls = bind_product.url_url_ids
        self.assertEqual(urls.model_id, bind_product)
        bind_product.write({"active": False})

        bind_product.flush()
        self.assertEqual(urls.model_id, bind_categ2)
        bind_product.write({"active": True})

        bind_product.flush()
        self.assertEqual(urls.model_id, bind_product)

    @contextmanager
    def _check_correct_unbind_active(self, variants):
        """
        During the execution of some cases, check the value of
        shopinvader products depending on related variants.
        If every variants are disabled => Shop. product should be disabled
        If at least 1 variant is enabled => Shop. product should be enabled
        :param variants: shopinvader.variant recordset
        :return:
        """
        variants = variants.with_context(active_test=False)
        # Save if the shopinvader product is active or not
        yield
        for variant in variants:
            shopinv_product = variant.shopinvader_product_id
            all_variants = shopinv_product.shopinvader_variant_ids
            # If all variants are disabled, the product should be disabled too.
            variants_disabled = all([not a.active for a in all_variants])
            if variants_disabled:
                self.assertFalse(shopinv_product.active)
                self._check_category_after_unbind(shopinv_product)
            # But if at least 1 is active, the product should stay into his
            # previous state.
            else:
                self.assertTrue(shopinv_product.active)

    def _check_category_after_unbind(self, shopinv_product):
        """
        When the product has been disabled, existing url should be
        a redirect to the category.
        :param shopinv_product: shopinvader.product recordset
        :return: bool
        """
        category = fields.first(
            shopinv_product.shopinvader_categ_ids.filtered(
                lambda c: c.active and not c.shopinvader_child_ids
            )
        )
        if category:
            for url in shopinv_product.url_url_ids:
                self.assertTrue(url.redirect)
                self.assertEqual(url.model_id, category)
        return True

    def test_unbind_variant(self):
        """
        For this test, we check the behavior during unbind of a
        shopinvader.variant.
        If every variants of a shopinvader.product are disabled (active False),
        we have to also disable the product.
        :return:
        """
        shopinv_product = self.shopinvader_variants.mapped("shopinvader_product_id")
        self.assertEqual(len(shopinv_product), 1)
        self.assertGreaterEqual(len(self.shopinvader_variants), 1)
        # Init: every variants and shopinv product are active True
        self.shopinvader_variants.write({"active": True})
        shopinv_product.write({"active": True})
        # Disable every variants
        with self._check_correct_unbind_active(self.shopinvader_variants):
            self.shopinvader_variants.write({"active": False})
        # Re-enable variants
        with self._check_correct_unbind_active(self.shopinvader_variants):
            self.shopinvader_variants.write({"active": True})
        # Re-enable also the shopinvader product
        shopinv_product.write({"active": True})
        # Disable only 1 variant
        with self._check_correct_unbind_active(self.shopinvader_variants):
            fields.first(self.shopinvader_variants).write({"active": False})

    def test_get_invader_variant(self):
        lang = self._install_lang("base.lang_fr")
        self.backend.lang_ids |= lang
        prod = self.env.ref("product.product_product_4b")
        self._bind_products(prod)
        variant_en = prod.shopinvader_bind_ids.filtered(
            lambda x: x.lang_id.code == "en_US"
        )
        variant_fr = prod.shopinvader_bind_ids.filtered(
            lambda x: x.lang_id.code == "fr_FR"
        )
        self.assertEqual(prod._get_invader_variant(self.backend, "en_US"), variant_en)
        self.assertEqual(prod._get_invader_variant(self.backend, "fr_FR"), variant_fr)

    def test_create_product_template_with_bindings(self):
        """
        Ensure the product bindings are created in a correct state,
        if they are created during a call to product.template.create()
        """
        vals_binding = [
            (
                0,
                0,
                {
                    "backend_id": self.backend.id,
                    "lang_id": self.env.ref("base.lang_en").id,
                },
            )
        ]
        vals_product = {"name": "aNewProduct", "shopinvader_bind_ids": vals_binding}
        product = self.env["product.template"].create(vals_product)
        self.assertEqual(len(product.shopinvader_bind_ids.ids), 1)
        self.assertTrue(product.shopinvader_bind_ids.active)

    # TODO: split this and other computed field tests to its own class
    def test_main_product(self):
        invader_variants = self.shopinvader_variants
        tmpl = invader_variants[0].product_tmpl_id
        main_variant = tmpl.product_variant_ids[0]
        self.assertTrue(
            invader_variants.filtered(lambda x: x.record_id == main_variant).main
        )
        self.assertNotIn(
            True,
            invader_variants.filtered(lambda x: x.record_id != main_variant).mapped(
                "main"
            ),
        )
        # change order
        tmpl.product_variant_ids[0].default_code = "ZZZZZZZ"
        tmpl.product_variant_ids[0].name = "ZZZZZZ"
        tmpl.product_variant_ids.invalidate_cache()
        main_variant1 = tmpl.product_variant_ids[0]
        self.assertNotEqual(main_variant, main_variant1)
        self.assertTrue(
            invader_variants.filtered(lambda x: x.record_id == main_variant1).main
        )
        self.assertNotIn(
            True,
            invader_variants.filtered(lambda x: x.record_id != main_variant1).mapped(
                "main"
            ),
        )

    def test_create_shopinvader_category_from_product_category(self):
        categ = self.env["product.category"].search([])[0]
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        categ.write(
            {
                "shopinvader_bind_ids": [
                    (
                        0,
                        0,
                        {
                            "backend_id": self.backend.id,
                            "lang_id": lang.id,
                            "seo_title": False,
                            "active": True,
                        },
                    )
                ]
            }
        )
