# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _delete_item(self, cart, params):
        """Overwrite method to delete child product packs when pack is not modifiable"""
        item = self._get_cart_item(cart, params, raise_if_not_found=False)
        if item.pack_child_line_ids and not item.pack_modifiable:
            item.pack_child_line_ids.unlink()
        if item:
            item.unlink()

    def _check_existing_cart_item(self, cart, params):
        order_lines = super()._check_existing_cart_item(cart, params)
        return order_lines.filtered(lambda l: not l.pack_parent_line_id)
