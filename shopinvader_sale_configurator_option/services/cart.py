# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from werkzeug.exceptions import NotFound


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def add_item_option(self, _id, **params):
        """
        Add an option to an order line item.
        _id is the line item id.
        """
        cart = self._get(create_if_not_found=False)
        if not cart:
            raise UserError("Can't add option to an empty cart.")

        product_line = cart.lines.search([("id", "=", _id)])
        if not product_line:
            raise NotFound("Order line not found for id: %s." % _id)

        product = product_line.product_id

        if not product:
            raise NotFound("No product is associated to this order line.")

        if not product.is_configurable_opt:
            raise UserError("Product %s is not configurable by options." % product.name)

        option = self.env["product.product"].browse(params["product_id"])

        if not option:
            raise NotFound("No product found for id %s." % params["product_id"])

        if not option.is_option:
            raise UserError("Product %s is not an option." % option.name)

        if option.id not in product.mapped("configurable_option_ids.product_id").ids:
            raise UserError(
                "Option %s is not an option of %s." % (option.name, product.name)
            )

        params.update(
            {
                "parent_option_id": product_line.id,
                "option_unit_qty": params["item_qty"],
                "child_type": "option",
                "parent_id": product_line.id,
            }
        )
        self._add_item(cart, params)
        cart.sync_sequence()

        return self._to_json(cart)

    def _prepare_cart_item(self, params, cart):
        cart_item = super()._prepare_cart_item(params, cart)
        if "child_type" in params:
            cart_item.update(
                {
                    "parent_option_id": params["parent_option_id"],
                    "option_unit_qty": params["option_unit_qty"],
                    "child_type": params["child_type"],
                    "parent_id": params["parent_id"],
                }
            )
        return cart_item

    def _validator_add_item_option(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "item_qty": {"coerce": float, "required": True, "type": "float"},
        }
