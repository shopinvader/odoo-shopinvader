# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import exceptions
from odoo.tools import mute_logger

from odoo.addons.shopinvader_restapi.tests.common import CommonCase
from odoo.addons.shopinvader_restapi.tests.test_cart_item import ItemCaseMixin


class ItemCase(ItemCaseMixin, CommonCase):
    @mute_logger("odoo.models.unlink")
    def test_add_item_with_product_not_allowed(self):
        self.env = self.env(
            context=dict(self.env.context, test_check_shopinvader_product=True)
        )
        self._setup_products()
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

        with self.assertRaises(exceptions.UserError):
            self.add_item(self.product_1.id, 1)
