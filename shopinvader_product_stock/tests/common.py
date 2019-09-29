# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tests.models import SeBackendFake
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBaseFake,
)
from odoo.addons.queue_job.tests.common import JobMixin


class StockCommonCase(TestBindingIndexBaseFake, JobMixin):
    def setUp(self):
        super(StockCommonCase, self).setUp()
        ref = self.env.ref
        self.shopinvader_backend = ref("shopinvader.backend_1")
        self.warehouse_1 = ref("stock.warehouse0")
        self.loc_1 = self.warehouse_1.lot_stock_id
        self.warehouse_2 = ref("stock.stock_warehouse_shop0")
        self.loc_2 = self.warehouse_2.lot_stock_id
        self.product = ref("product.product_product_4")
        self.shopinvader_backend.bind_all_product()
        self.index = self.env["se.index"].create(
            {
                "name": "test-product-index",
                "backend_id": self.backend_specific.se_backend_id.id,
                "exporter_id": ref(
                    "shopinvader.ir_exp_shopinvader_variant"
                ).id,
                "lang_id": ref("base.lang_en").id,
                "model_id": ref("shopinvader.model_shopinvader_variant").id,
            }
        )
        self.shopinvader_backend.write(
            {
                "se_backend_id": self.backend_specific.se_backend_id.id,
                "warehouse_ids": [(6, 0, self.warehouse_1.ids)],
                "product_stock_field_id": ref(
                    "stock.field_product_product__qty_available"
                ).id,
            }
        )
        self.loc_supplier = self.env.ref("stock.stock_location_suppliers")
        self.picking_type_in = self.env.ref("stock.picking_type_in")

    @classmethod
    def setUpClass(cls):
        super(StockCommonCase, cls).setUpClass()
        SeBackendFake._test_setup_model(cls.env)
        cls._create_se_backend_fake_acl()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
                test_queue_job_no_delay=False,  # we want the jobs
            )
        )

    @classmethod
    def tearDownClass(cls):
        # Seems not necessary
        # SeBackendFake._test_teardown_model(cls.env)
        super().tearDownClass()

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "new_quantity": qty,
                "location_id": location.id,
            }
        )
        wizard.change_product_qty()

    def _create_incomming_move(self):
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

    @classmethod
    def _create_se_backend_fake_acl(cls):
        model_id = cls._test_get_model_id(SeBackendFake._name)
        values = {
            "name": "Fake ACL for %s" % SeBackendFake._name,
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
