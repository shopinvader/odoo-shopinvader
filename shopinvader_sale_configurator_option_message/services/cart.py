# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _prepare_cart_item(self, params, cart):
        cart_item = super()._prepare_cart_item(params, cart)
        if "message" in params:
            cart_item.update(
                {
                    "option_message": params["message"],
                }
            )
        return cart_item

    def _validator_add_item_option(self):
        schema = super()._validator_add_item_option()
        schema.update(
            {
                "message": {"type": "string"},
            }
        )
        return schema

    def _upgrade_cart_item_quantity_vals(self, item, params, action="replace"):
        vals = super()._upgrade_cart_item_quantity_vals(
            item, params, "replace" if "message" in params else action
        )

        if "message" in params:
            vals["option_message"] = params["message"]

        return vals
