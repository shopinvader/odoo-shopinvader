# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .test_cart import CommonConnectedCartCase


class TestCartCopy(CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super(TestCartCopy, cls).setUpClass()
        cls.product_copy = cls.env.ref("product.product_product_24")
        cls.product_copy.list_price = 500.0

    @mute_logger("odoo.models.unlink")
    def test_cart_copy(self):
        # Copy existing cart
        # Check if we return a new one with new values
        result = self.service.dispatch("copy", params={"id": self.cart.id})
        cart_data = result.get("data")
        new_id = cart_data.get("id")
        self.assertNotEqual(new_id, self.cart.id)
        copy_cart = self.env["sale.order"].browse(new_id)
        self.assertEqual("cart", copy_cart.typology)
        line = copy_cart.order_line.filtered(
            lambda l: l.product_id == self.product_copy
        )
        self.assertEqual(500.0, line.price_unit)

    @mute_logger("odoo.models.unlink")
    def test_cart_copy_does_not_exist(self):
        cart_id = self.cart.id
        self.cart.unlink()
        # Check validator
        with self.assertRaises(UserError):
            self.service.dispatch("copy", params={"id": cart_id})
