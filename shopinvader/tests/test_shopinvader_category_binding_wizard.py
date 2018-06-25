# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.tests.common import SavepointComponentCase


class TestShopinvaderCategoryBindingWizard(SavepointComponentCase):

    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderCategoryBindingWizard, cls).setUpClass()
        cls.backend = cls.env.ref('shopinvader.backend_1')
        cls.product_category = cls.env.ref('product.product_category_4')
        cls.bind_wizard_model = cls.env[
            'shopinvader.category.binding.wizard']
        cls.unbind_wizard_model = cls.env[
            'shopinvader.category.unbinding.wizard']
        cls.category_bind_model = cls.env['shopinvader.category']

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
        bind_wizard = self.bind_wizard_model.create({
            'backend_id': backend.id,
            'product_category_ids': [(6, 0, product_category.ids)],
        })

        bind_wizard.action_bind_categories()
        domain = [
            ('record_id', '=', product_category.id),
            ('backend_id', '=', backend.id),
        ]

        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        self.assertEqual(len(bind_record), 1)
        self.assertEqual(bind_record, product_category.shopinvader_bind_ids)

        # --------------------------------
        # UnBind the category
        # --------------------------------
        unbind_wizard = unbind_wizard_model.create({
            'shopinvader_category_ids': [(6, 0, bind_record.ids)],
        })
        unbind_wizard.action_unbind_categories()

        # The binding record should be unreachable
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 0)

        # The binding record should still exist but inactive
        bind_record = category_bind_model.with_context(
            active_test=False).search(domain)

        self.assertEqual(len(bind_record), 1)

        # --------------------------------
        # Bind the category again
        # --------------------------------
        values = {
            'backend_id': backend.id,
            'product_category_ids': [(6, 0, product_category.ids)],
        }
        # Active test because product.category is active = False
        bind_wizard = bind_wizard_model.with_context(
            active_test=False).create(values)
        bind_wizard.action_bind_categories()

        # The binding record should be re-activated
        bind_record = self.category_bind_model.search(domain)
        self.assertEqual(len(bind_record), 1)

    def install_lang(self, lang_xml_id):
        lang = self.env.ref(lang_xml_id)
        wizard = self.env['base.language.install'].create({
            'lang': lang.code,
        })
        wizard.lang_install()
        return lang

    def test_category_binding_multi_lang(self):
        """
        With more than 1 lang, select a category and
        - bind it to a shopinvader backend
        - unbind it
        - bind it again
        """
        lang = self.install_lang('base.lang_fr')
        self.backend.lang_ids |= lang
        category_bind_model = self.category_bind_model
        unbind_wizard_model = self.unbind_wizard_model
        bind_wizard_model = self.bind_wizard_model
        product_category = self.product_category
        backend = self.backend
        self.assertFalse(product_category.shopinvader_bind_ids)

        # --------------------------------
        # Bind the category to the Backend
        # --------------------------------
        bind_wizard = self.bind_wizard_model.create({
            'backend_id': backend.id,
            'product_category_ids': [(6, 0, product_category.ids)],
        })
        bind_wizard.action_bind_categories()
        domain = [
            ('record_id', '=', product_category.id),
            ('backend_id', '=', backend.id),
        ]

        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        # 2 (because 2 languages installed)
        self.assertEqual(len(bind_record), 2)
        self.assertEqual(bind_record, product_category.shopinvader_bind_ids)

        # --------------------------------
        # UnBind the category
        # --------------------------------
        unbind_wizard = unbind_wizard_model.create({
            'shopinvader_category_ids': [(6, 0, bind_record.ids)],
        })
        unbind_wizard.action_unbind_categories()

        # The binding record should be unreachable
        bind_record = category_bind_model.search(domain)

        self.assertEqual(len(bind_record), 0)

        # The binding record should still exist but inactive
        bind_record = category_bind_model.with_context(
            active_test=False).search(domain)

        self.assertEqual(len(bind_record), 2)

        # --------------------------------
        # Bind the category again
        # --------------------------------
        values = {
            'backend_id': backend.id,
            'product_category_ids': [(6, 0, product_category.ids)],
        }
        # Active test because product.category is active = False
        bind_wizard = bind_wizard_model.with_context(
            active_test=False).create(values)
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
        bind_wizard = bind_wizard_model.create({
            'backend_id': backend.id,
            'product_category_ids': [(6, 0, product_category.ids)],
        })
        bind_wizard.action_bind_categories()

        domain = [
            ('record_id', '=', product_category.id),
            ('backend_id', '=', backend.id),
        ]
        # A binding record should exists
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 1)

        # --------------------------------
        # Inactivate the category
        # --------------------------------
        product_category.write({'active': False})

        # The binding record should be unreachable
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 0)

        # --------------------------------
        # Re-activate the category
        # --------------------------------
        product_category.write({'active': True})

        # The binding record should be still unreachable
        nb_bind_record = category_bind_model.search_count(domain)

        self.assertEqual(nb_bind_record, 0)
        bind_wizard.action_bind_categories()
        # A binding record should exists
        bind_record = category_bind_model.search(domain)
        self.assertTrue(bind_record)
        # Disable the category and the binded record should be disabled too
        product_category.write({'active': False})
        self.assertFalse(bind_record.active)
