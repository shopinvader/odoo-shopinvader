# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tests.models import SeBackendFake
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBaseFake,
)
from odoo.addons.shopinvader.tests.common import CommonMixin


class StockCommonCase(TestBindingIndexBaseFake, CommonMixin):
    def setUp(self):
        super(StockCommonCase, self).setUp()
        ref = self.env.ref
        self.shopinvader_backend = ref("shopinvader.backend_1")
        self.warehouse_1 = ref("stock.warehouse0")
        self.loc_1 = self.warehouse_1.lot_stock_id
        self.warehouse_2 = self.env['stock.warehouse'].create({
            'name': 'Warehouse 2',
            'code': 'WH2',
            'company_id': self.env.ref('base.main_company').id
        })
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

    def _init_stock_to_zero(self, product, location):
        self._add_stock_to_product(product, location, 0)

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        inventory = self.env['stock.inventory'].create({
            'location_ids': [(4, location.id)],
            'product_ids': [(4, product.id)],
        })
        inventory.action_start()
        if inventory.line_ids:
            inventory.line_ids = False
        inventory.write({'line_ids': [(0, 0, {
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'product_qty': qty,
            'location_id': location.id
        })]
                         })
        inventory.action_validate()

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
