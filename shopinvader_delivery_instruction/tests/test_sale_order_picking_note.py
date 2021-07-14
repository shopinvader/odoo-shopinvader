# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleOrderDeliveryNote(CommonCase):
    """
    Tests about the delivery note provided by the customer.
    This field should by passed into the related picking.
    """

    def setUp(self):
        super().setUp()
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_1")
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_update_picking_note1(self):
        """
        Execute some update on existing cart (update many times the
        delivery_instruction) then confirm it to check if the
        delivery_instruction is passed to related pickings.
        :return:
        """
        delivery_instructions = [
            str(uuid4()),
            str(uuid4()),
            "",
            "",
            str(uuid4()),
            str(uuid4()),
        ]
        for delivery_instruction in delivery_instructions:
            params = {"delivery_instruction": delivery_instruction}
            self.service.dispatch("update", params=params)
            self.assertEqual(self.cart.picking_note, delivery_instruction)
        result = self.service.dispatch("update")
        data = result.get("data", {})
        self.assertEqual(data.get("delivery_instruction"), delivery_instruction)
        self.cart.action_confirm()
        pickings = self.cart.picking_ids
        self.assertTrue(pickings)
        for picking in pickings:
            # Should be equals to the last delivery_instruction set on the cart
            self.assertEqual(picking.note, delivery_instruction)
        return
