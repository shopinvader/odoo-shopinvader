# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import exceptions
from odoo.tools import mute_logger

from odoo.addons.shopinvader_v1_base.tests.test_cart_item import ItemCaseMixin


class AbstractItemCase(ItemCaseMixin):
    @classmethod
    def setUpClass(cls):
        super(AbstractItemCase, cls).setUpClass()
        cls._setup_products()

    @mute_logger("odoo.models.unlink")
    def test_add_item_with_product_not_allowed(self):
        self.remove_cart()
        with self.assertRaises(exceptions.UserError):
            self.add_item(self.product_1.id, 1)
