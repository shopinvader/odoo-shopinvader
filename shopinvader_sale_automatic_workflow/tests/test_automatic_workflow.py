# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from odoo.addons.shopinvader_v1_base.tests.test_cart import CommonConnectedCartCase


class TestShopinvaderOrderSaleWorkflow(CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.workflow_process_id = cls.env["sale.workflow.process"].create(
            {"name": "Test Workflow"}
        )

    @mute_logger("odoo.models.unlink")
    def test_cart_create(self):
        self.cart.unlink()
        cart = self.service._get()
        self.assertRecordValues(
            cart,
            [
                {
                    "workflow_process_id": self.backend.workflow_process_id.id,
                }
            ],
        )
