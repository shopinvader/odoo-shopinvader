# -*- coding: utf-8 -*-
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
    _collection = "shopinvader.api.v2"

    @restapi.method(
        [(["/set_carrier"], "POST")],
        input_param=restapi.CerberusValidator("_set_carrier_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
    )
    def set_carrier(self, **params):
        """
           This service will set the given delivery method to the current
           cart
       """
        cart = self._find_open_cart(uuid=params.get("uuid"))
        if not cart:
            raise NotFound("No cart found")
        else:
            self._set_carrier(cart, params["carrier_id"])
            return self._response_for_cart(cart)

    # #######
    # schemas
    # #######

    def _set_carrier_input_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True},
            "carrier_id": {
                "coerce": int,
                "nullable": True,
                "required": True,
                "type": "integer",
            },
        }

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["delivery"] = {
            "type": "dict",
            "schema": self._delivery_output_schema,
            "required": False,
            "nullable": True,
        }
        return schema

    @property
    def _delivery_output_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "code": {"type": "string", "required": False, "nullable": True},
            "name": {"type": "string", "required": True, "nullable": False},
            "description": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
            "amount": {
                "type": "dict",
                "required": True,
                "nullable": False,
                "schema": self._delivery_amount_output_schema,
            },
        }

    @property
    def _delivery_amount_output_schema(self):
        return {
            "tax": {"type": "float", "required": True, "nullable": False},
            "untaxed": {"type": "float", "required": True, "nullable": False},
            "total": {"type": "float", "required": True, "nullable": False},
        }

    @property
    def _amount_output_schema(self):
        schema = super(CartService, self)._amount_output_schema
        schema.update(
            {
                "tax_without_shipping": {
                    "type": "float",
                    "required": True,
                    "nullable": False,
                },
                "untaxed_without_shipping": {
                    "type": "float",
                    "required": True,
                    "nullable": False,
                },
                "total_without_shipping": {
                    "type": "float",
                    "required": True,
                    "nullable": False,
                },
                "total_without_shipping_without_discount": {
                    "type": "float",
                    "required": True,
                    "nullable": False,
                },
            }
        )
        return schema

    # ##############
    # implementation
    # ##############

    def _set_carrier(self, cart, carrier_id):
        if carrier_id not in [x["id"] for x in cart._get_available_carrier()]:
            raise UserError(
                _("This delivery method is not available for you order")
            )
        cart.write({"carrier_id": carrier_id})
        cart.delivery_set()

    def _is_line(self, line):
        res = super(CartService, self)._is_line(line)
        return res and not line.is_delivery

    def _convert_amount(self, sale):
        amounts = super(CartService, self)._convert_amount(sale)
        precision = sale.currency_id.decimal_places
        tax = amounts["tax"] - sale.shipping_amount_tax
        untaxed = amounts["untaxed"] - sale.shipping_amount_untaxed
        total = amounts["total"] - sale.shipping_amount_total
        total_without_shipping = total - sale.discount_total
        amounts.update(
            {
                "tax_without_shipping": float_round(tax, precision),
                "untaxed_without_shipping": float_round(untaxed, precision),
                "total_without_shipping": float_round(total, precision),
                "total_without_shipping_without_discount": float_round(
                    total_without_shipping, precision
                ),
            }
        )
        return amounts

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["delivery"] = self._convert_delivery_to_json(sale)
        return json

    def _convert_delivery_to_json(self, sale):
        return {
            "id": sale.carrier_id.id,
            "name": sale.carrier_id.name,
            "description": sale.carrier_id.description or None,
            "code": sale.carrier_id.code or None,
            "amount": self._convert_delivery_amount_to_json(sale),
        }

    def _convert_delivery_amount_to_json(self, sale):
        precision = sale.currency_id.decimal_places
        return {
            "tax": float_round(sale.shipping_amount_tax, precision),
            "untaxed": float_round(sale.shipping_amount_untaxed, precision),
            "total": float_round(sale.shipping_amount_total, precision),
        }
