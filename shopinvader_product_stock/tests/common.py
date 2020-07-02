# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBaseFake,
)

from odoo.addons.queue_job.tests.common import JobMixin
from odoo_test_helper import FakeModelLoader


class StockCommonCase(TestBindingIndexBaseFake, JobMixin):

    @classmethod
    def setUpClass(cls):
        super(StockCommonCase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
                test_queue_job_no_delay=False,  # we want the jobs
            )
        )
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackendFake
        cls.loader.update_registry(
            (SeBackendFake, )
        )
        cls._create_fake_acl(SeBackendFake)
        ref = cls.env.ref
        cls.shopinvader_backend = ref("shopinvader.backend_1")
        cls.warehouse_1 = ref("stock.warehouse0")
        cls.loc_1 = cls.warehouse_1.lot_stock_id
        cls.warehouse_2 = ref("stock.stock_warehouse_shop0")
        cls.loc_2 = cls.warehouse_2.lot_stock_id
        cls.product = cls.env["product.product"].create({"name": "Stock prod 1", "type": "product"})
        cls.shopinvader_backend.bind_all_product()
        cls.index = cls.env["se.index"].create(
            {
                "name": "test-product-index",
                "backend_id": cls.backend_specific.se_backend_id.id,
                "exporter_id": ref(
                    "shopinvader.ir_exp_shopinvader_variant"
                ).id,
                "lang_id": ref("base.lang_en").id,
                "model_id": ref("shopinvader.model_shopinvader_variant").id,
            }
        )
        cls.shopinvader_backend.write(
            {
                "se_backend_id": cls.backend_specific.se_backend_id.id,
                "warehouse_ids": [(6, 0, cls.warehouse_1.ids)],
                "product_stock_field_id": ref(
                    "stock.field_product_product__qty_available"
                ).id,
            }
        )
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")


    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(StockCommonCase, cls).tearDownClass()

    def _add_stock_to_product(self, product, location, qty):
        """Set the stock quantity of the product.

        :param product: product.product recordset
        :param qty: float
        """
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': product.id,
            'location_id': location.id,
            'inventory_quantity': qty,
        })

    def _create_incoming_move(self):
        location_dest = self.picking_type_in.default_location_dest_id
        return self.env["stock.move"].create(
            {
                "name": "Forced Move",
                "location_id": self.loc_supplier.id,
                "location_dest_id": location_dest.id,
                "product_id": self.product.id,
                "product_uom_qty": 2.0,
                "product_uom": self.product.uom_id.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )

    # TODO: this should be move to test helper
    @classmethod
    def _create_fake_acl(cls, Klass):
        model_id = cls._test_get_model_id(Klass._name)
        values = {
            "name": "Fake ACL for %s" % Klass._name,
            "model_id": model_id,
            "perm_read": 1,
            "perm_create": 1,
            "perm_write": 1,
            "perm_unlink": 1,
            "active": True,
        }
        cls.env["ir.model.access"].create(values)

    @classmethod
    def _test_get_model_id(cls, name):
        cls.env.cr.execute("SELECT id FROM ir_model WHERE model = %s", (name,))
        res = cls.env.cr.fetchone()
        return res[0] if res else None
