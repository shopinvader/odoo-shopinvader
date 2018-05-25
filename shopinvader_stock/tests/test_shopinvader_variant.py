# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from random import randint
import mock
from odoo import api, models
from odoo.fields import first
from odoo.addons.component.tests.common import SavepointComponentCase


class TestSeBackend(models.Model):
    _name = 'test.se.backend'
    _inherit = 'se.backend.spec.abstract'
    _description = 'Unit Test SE Backend'

    def init(self):
        self.env['se.backend'].register_spec_backend(self)

    def _register_hook(self):
        self.env['se.backend'].register_spec_backend(self)


class TestShopinvaderVariant(SavepointComponentCase):
    """
    Tests for shopinvader.variant
    """

    def _init_test_model(self, model_cls):
        """
        Function to init/create a new Odoo Model during unit test.
        Based on base_kanban_stage/test/test_base_kanban_abstract.py
        :param model_cls: Odoo Model class
        :return: instance of model (empty)
        """
        registry = self.env.registry
        registry.enter_test_mode()
        cr = self.env.cr
        model_cls._build_model(registry, cr)
        model = self.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return self.env[model_cls._name]

    def setUp(self):
        super(TestShopinvaderVariant, self).setUp()
        # To load a new Model, we have to use a new cursor and env.
        # Because there is a commit on the model._auto_init()
        # Based on base_kanban_stage/test/test_base_kanban_abstract.py
        # self.registry.enter_test_mode()
        # self.old_cursor = self.cr
        # self.cr = self.registry.cursor()
        self.cr.commit = mock.MagicMock()
        self.env = api.Environment(self.cr, self.uid, {})
        self.shopinvader_backend = self.env.ref('shopinvader.backend_1')
        self.shopinvader_backend.bind_all_product()
        test_se_backend_obj = self._init_test_model(TestSeBackend)
        self.test_model = test_se_backend_obj
        self.wizard_stock_obj = self.env['stock.change.product.qty']
        self.test_se_backend_obj = test_se_backend_obj
        # The target field is 'qty_available' on product.product
        # This one is used into these tests.
        # Please don't change it (or change it everywhere)
        field_qty_available = self.env.ref(
            "stock.field_product_product_qty_available")
        backend_values = {
            'product_stock_field_id': field_qty_available.id,
            'export_stock_key': str(uuid4()),
            'specific_model': test_se_backend_obj._name,
        }
        self.backend = backend = test_se_backend_obj.create(backend_values)
        self.shopinvader_backend.write({
            'se_backend_id': backend.se_backend_id.id,
        })
        self.product_tmpl = self.env.ref(
            'product.product_product_4_product_template')

    def tearDown(self):
        self.registry.leave_test_mode()
        test_model = self.test_model
        selection = (test_model._name, test_model._description)
        self.env[test_model._name]._fields.get('specific_model').selection(
            test_model).remove(selection)
        super(TestShopinvaderVariant, self).tearDown()

    def _add_stock_to_product(self, product, qty=10):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        :return: bool
        """
        wizard_obj = self.wizard_stock_obj
        wizard = wizard_obj.create({
            'product_id': product.id,
            'new_quantity': qty,
        })
        wizard.change_product_qty()
        return True

    def test_get_se_backend_stock_value1(self):
        """
        Test the function _get_se_backend_stock_value() on shopinvader.variant.
        This function should return the value based on the stock field set on
        the related backend.
        For example, if we set the 'qty_available' field on the backend,
        the function should return the value of this field (applied on the
        shopinvader.variant) so like if we
        did shopinvader_variant.qty_available
        :return: float
        """
        backend = self.backend
        se_backend = backend.se_backend_id
        product_tmpl = self.product_tmpl
        shopinvader_variants = product_tmpl.product_variant_ids.mapped(
            "shopinvader_bind_ids")
        shopinvader_variants = shopinvader_variants.filtered(
            lambda v: v.backend_id.se_backend_id.id == se_backend.id)
        shopinvader_variant = first(shopinvader_variants)
        product_product = shopinvader_variant.record_id
        qty = randint(2, 1000)
        self._add_stock_to_product(product_product, qty=qty)
        # Ensure that the qty is updated
        self.assertAlmostEqual(product_product.qty_available, qty)
        dynamic_qty = shopinvader_variant._get_se_backend_stock_value()
        self.assertAlmostEqual(dynamic_qty, qty)
        # Re-update the quantity
        qty = randint(2, 1000)
        self._add_stock_to_product(product_product, qty=qty)
        # Ensure that the qty is updated, again
        self.assertAlmostEqual(product_product.qty_available, qty)
        shopinvader_variant.refresh()
        dynamic_qty = shopinvader_variant._get_se_backend_stock_value()
        self.assertAlmostEqual(dynamic_qty, qty)
        return True

    def test_update_stock_qty_sent1(self):
        """
        Test the function _update_stock_qty_sent() on shopinvader.variant.
        This function should update the field last_stock_value on
        shopinvader.variant with the given quantity.
        :return: float
        """
        backend = self.backend
        se_backend = backend.se_backend_id
        product_tmpl = self.product_tmpl
        shopinvader_variants = product_tmpl.product_variant_ids.mapped(
            "shopinvader_bind_ids")
        shopinvader_variants = shopinvader_variants.filtered(
            lambda v: v.backend_id.se_backend_id.id == se_backend.id)
        shopinvader_variant = first(shopinvader_variants)
        # Put an empty value
        shopinvader_variant.write({
            'last_stock_value': 0,
        })
        qty = randint(2, 1000)
        shopinvader_variant._update_stock_qty_sent(qty)
        self.assertAlmostEqual(shopinvader_variant.last_stock_value, qty)
        qty = randint(2, 1000)
        shopinvader_variant._update_stock_qty_sent(qty)
        self.assertAlmostEqual(shopinvader_variant.last_stock_value, qty)
        qty = randint(2, 1000)
        shopinvader_variant._update_stock_qty_sent(qty)
        self.assertAlmostEqual(shopinvader_variant.last_stock_value, qty)
        return True
