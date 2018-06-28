# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from random import randint
from contextlib import contextmanager
import mock
from odoo import api, models
from odoo.addons.component.tests.common import SavepointComponentCase


@contextmanager
def mock_work_on(se_backend):
    """
    Replace the return value of the function 'work_on' by a lambda fct
    :param se_backend: se.backend recordset
    :return:
    """
    fct = 'work_on'
    with mock.patch.object(se_backend.__class__, fct) as mocked_fct:
        mocked_fct.return_value = mock.MagicMock()
        yield


class TestSeBackend(models.Model):
    _name = 'test.se.backend'
    _inherit = 'se.backend.spec.abstract'
    _description = 'Unit Test SE Backend'

    def init(self):
        self.env['se.backend'].register_spec_backend(self)

    def _register_hook(self):
        self.env['se.backend'].register_spec_backend(self)


class TestStockMove(SavepointComponentCase):
    """
    Tests for stock.move
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
        super(TestStockMove, self).setUp()

        self.cr.commit = mock.MagicMock()
        self.env = api.Environment(self.cr, self.uid, {})
        test_se_backend_obj = self._init_test_model(TestSeBackend)
        self.test_model = test_se_backend_obj
        self.test_se_backend_obj = test_se_backend_obj
        self.wizard_stock_obj = self.env['stock.change.product.qty']
        self.shopinvader_backend = self.env.ref('shopinvader.backend_1')
        # se_backend_obj = self.env['se.backend']
        field_qty_available = self.env.ref(
            "stock.field_product_product_qty_available")
        lang_en = self.env.ref("base.lang_en")
        shopinvader_variant_model = self.env.ref(
            "shopinvader_product_stock.model_shopinvader_variant")
        index_values = {
            'name': 'Index EN test',
            'lang_id': lang_en.id,
            'model_id': shopinvader_variant_model.id,
        }
        # For these tests, add the normal se.backend
        # test_se_backend_obj.register_spec_backend(se_backend_obj)
        backend_values = {
            'product_stock_field_id': field_qty_available.id,
            'export_stock_key': str(uuid4()),
            'specific_model': test_se_backend_obj._name,
            'index_ids': [
                (0, False, index_values),
            ]
        }
        self.backend = backend = test_se_backend_obj.create(backend_values)

        self.shopinvader_backend.write({
            'se_backend_id': backend.se_backend_id.id,
        })

        self.shopinvader_backend.bind_all_product()
        self.move_obj = self.env['stock.move']
        self.product_obj = self.env['product.product']
        self.job_obj = self.env['queue.job']
        self.loc_supplier = self.env.ref('stock.stock_location_suppliers')
        self.product = self.env.ref('product.product_product_8')
        self.picking_type_in = self.env.ref("stock.picking_type_in")

    def tearDown(self):
        self.registry.leave_test_mode()
        test_model = self.test_model
        selection = (test_model._name, test_model._description)
        self.env[test_model._name]._fields.get('specific_model').selection(
            test_model).remove(selection)
        super(TestStockMove, self).tearDown()

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

    def test_action_cancel1(self):
        """
        Test the function action_cancel() on stock.move who should create a
        new queue.job
        :return:
        """
        move_obj = self.move_obj
        job_obj = self.job_obj
        picking_type_in = self.picking_type_in
        loc_supplier = self.loc_supplier
        product = self.product
        values = {
            'name': 'Forced Move',
            'location_id': loc_supplier.id,
            'location_dest_id': picking_type_in.default_location_dest_id.id,
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'product_uom': product.uom_id.id,
            'picking_type_id': picking_type_in.id,
        }
        move = move_obj.create(values)
        job_name = 'Update shopinvader variants (stock update trigger)'
        domain_queue_job = [
            ('name', 'ilike', job_name),
        ]
        nb_job_before = job_obj.search_count(domain_queue_job)
        move.action_cancel()
        nb_job_after = job_obj.search_count(domain_queue_job)
        self.assertGreater(nb_job_after, nb_job_before)
        return True

    def test_action_confirm1(self):
        """
        Test the function action_confirm() on stock.move who should create a
        new queue.job
        :return:
        """
        move_obj = self.move_obj
        job_obj = self.job_obj
        picking_type_in = self.picking_type_in
        loc_supplier = self.loc_supplier
        product = self.product
        values = {
            'name': 'Forced Move',
            'location_id': loc_supplier.id,
            'location_dest_id': picking_type_in.default_location_dest_id.id,
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'product_uom': product.uom_id.id,
            'picking_type_id': picking_type_in.id,
        }
        move = move_obj.create(values)
        job_name = 'Update shopinvader variants (stock update trigger)'
        domain_queue_job = [
            ('name', 'ilike', job_name),
        ]
        nb_job_before = job_obj.search_count(domain_queue_job)
        move.action_confirm()
        nb_job_after = job_obj.search_count(domain_queue_job)
        self.assertGreater(nb_job_after, nb_job_before)
        return True

    def test_action_done1(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        move_obj = self.move_obj
        job_obj = self.job_obj
        picking_type_in = self.picking_type_in
        loc_supplier = self.loc_supplier
        product = self.product
        values = {
            'name': 'Forced Move',
            'location_id': loc_supplier.id,
            'location_dest_id': picking_type_in.default_location_dest_id.id,
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'product_uom': product.uom_id.id,
            'picking_type_id': picking_type_in.id,
        }
        move = move_obj.create(values)
        job_name = 'Update shopinvader variants (stock update trigger)'
        domain_queue_job = [
            ('name', 'ilike', job_name),
        ]
        nb_job_before = job_obj.search_count(domain_queue_job)
        move.action_done()
        nb_job_after = job_obj.search_count(domain_queue_job)
        self.assertGreater(nb_job_after, nb_job_before)
        return True

    def test_product_stock_update_all1(self):
        """
        Test the function _product_stock_update_all() on stock.move who should
        create 1 new queue.job per index (related to shopinvader.variant)
        :return:
        """
        move_obj = self.move_obj
        job_obj = self.job_obj
        picking_type_in = self.picking_type_in
        loc_supplier = self.loc_supplier
        product = self.product
        qty = randint(2, 1000)
        self._add_stock_to_product(product, qty=qty)
        values = {
            'name': 'Forced Move',
            'location_id': loc_supplier.id,
            'location_dest_id': picking_type_in.default_location_dest_id.id,
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'product_uom': product.uom_id.id,
            'picking_type_id': picking_type_in.id,
        }
        move = move_obj.create(values)
        job_name = 'Update shopinvader variants (stock trigger) on backend'
        domain_queue_job = [
            ('name', 'ilike', job_name),
        ]
        nb_job_before = job_obj.search_count(domain_queue_job)
        move.mapped("product_id")._product_stock_update_all()
        nb_job_after = job_obj.search_count(domain_queue_job)
        self.assertGreater(nb_job_after, nb_job_before)
        return True

    def test_product_stock_update_by_index1(self):
        """
        Test the function _product_stock_update_by_index() on stock.move.
        This one should run the export (not tested here) and also update
        the last quantity synchronized
        :return:
        """
        move_obj = self.move_obj
        product_obj = self.product_obj
        picking_type_in = self.picking_type_in
        loc_supplier = self.loc_supplier
        product = self.product
        qty = randint(2, 1000)
        self._add_stock_to_product(product, qty=qty)
        shopinvader_variant = \
            product_obj._get_shopinvader_variants_from_product(product)
        values = {
            'name': 'Forced Move',
            'location_id': loc_supplier.id,
            'location_dest_id': picking_type_in.default_location_dest_id.id,
            'product_id': product.id,
            'product_uom_qty': 2.0,
            'product_uom': product.uom_id.id,
            'picking_type_id': picking_type_in.id,
        }
        move = move_obj.create(values)
        mapper = product_obj._get_stock_mapper()
        spec_backend = shopinvader_variant.index_id.backend_id.specific_backend
        spec_backend.work_on = mock.MagicMock()
        expected_value = shopinvader_variant._get_se_backend_stock_value()
        with mock_work_on(spec_backend):
            move.mapped("product_id")._product_stock_update_by_index(
                shopinvader_variant, mapper)
        self.assertAlmostEqual(
            shopinvader_variant.last_stock_value, expected_value)
        return True
