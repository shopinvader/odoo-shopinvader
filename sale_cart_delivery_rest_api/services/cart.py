# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/set_delivery_method"], "POST")],
        input_param=restapi.CerberusValidator("_set_delivery_method_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
    )
    def set_delivery_method(self, **params):
        """
        This service will set the given delivery method to the current
        cart
        """
        cart = self._find_open_cart(uuid=params.get("uuid"))
        if not cart:
            raise NotFound("No cart found")
        else:
            self._set_delivery_method(cart, params)
            return self._response_for_cart(cart)

    # #######
    # schemas
    # #######

    def _set_delivery_method_input_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True},
            "method_id": {
                "coerce": int,
                "nullable": True,
                "required": True,
                "type": "integer",
            },
        }

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["amount_without_delivery"] = {
            "type": "dict",
            "schema": self._amount_output_schema,
            "required": False,
            "nullable": True,
        }
        return schema

    @property
    def _delivery_output_schema(self):
        schema = super(CartService, self)._delivery_output_schema
        schema.update(
            {
                "method": {
                    "type": "dict",
                    "schema": self._delivery_method_output_schema,
                    "required": False,
                    "nullable": True,
                },
                "fees": {
                    "type": "dict",
                    "schema": self._amount_output_schema,
                    "required": False,
                    "nullable": True,
                },
            }
        )
        return schema

    @property
    def _delivery_method_output_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "code": {"type": "string", "required": False, "nullable": True},
            "name": {"type": "string", "required": True, "nullable": False},
            "description": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
        }

    # ##############
    # implementation
    # ##############

    def _must_charge_delivery_fee_on_order(self):
        """Return true if the delivery fee must be set on the cart at
        the same time as the method or false if delivery fee are applied on
        delivery.
        """
        return True

    def _set_delivery_method(self, cart, params):
        method_id = params["method_id"]
        if not cart._is_delivery_method_available(method_id):
            raise UserError(_("This delivery method is not available for you order"))
        cart.write({"carrier_id": method_id})
        if self._must_charge_delivery_fee_on_order():
            cart.delivery_set()

    def _is_line(self, line):
        res = super(CartService, self)._is_line(line)
        return res and not line.is_delivery

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["amount_without_delivery"] = self._convert_amount_without_delivery(sale)
        return json

    def _convert_amount_without_delivery(self, sale):
        amounts = super(CartService, self)._convert_amount(sale)
        precision = sale.currency_id.decimal_places
        tax = sale.amount_tax - sale.shipping_amount_tax
        untaxed = sale.amount_untaxed - sale.shipping_amount_untaxed
        total = sale.discount_total - sale.shipping_amount_total
        total_without_discount = total - sale.discount_total
        amounts.update(
            {
                "tax": float_round(tax, precision),
                "untaxed": float_round(untaxed, precision),
                "total": float_round(total, precision),
                "total_without_discount": float_round(
                    total_without_discount, precision
                ),
            }
        )
        return amounts

    def _convert_delivery(self, sale):
        info = super(CartService, self)._convert_delivery(sale)
        info.update(
            {
                "method": {
                    "id": sale.carrier_id.id,
                    "name": sale.carrier_id.name,
                    "description": sale.carrier_id.description or None,
                    "code": sale.carrier_id.code or None,
                },
                "fees": self._convert_delivery_amount(sale),
            }
        )
        return info

    def _convert_delivery_amount(self, sale):
        precision = sale.currency_id.decimal_places
        total = float_round(sale.shipping_amount_total, precision)
        return {
            "tax": float_round(sale.shipping_amount_tax, precision),
            "untaxed": float_round(sale.shipping_amount_untaxed, precision),
            "total": total,
            "total_without_discount": total,
            "discount_total": 0.0,
        }
