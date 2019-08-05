# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo.addons.component.core import AbstractComponent, Component
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_shipping(self, cart):
        res = super()._convert_shipping(cart)
        selected_carrier = {}
        if cart.carrier_id:
            carrier = cart.carrier_id
            selected_carrier = {
                "id": carrier.id,
                "name": carrier.name,
                "description": carrier.name,
            }
        res.update(
            {
                "amount": {
                    "tax": cart.shipping_amount_tax,
                    "untaxed": cart.shipping_amount_untaxed,
                    "total": cart.shipping_amount_total,
                },
                "selected_carrier": selected_carrier,
            }
        )
        return res

    def _convert_amount(self, sale):
        """
        Inherit to add amounts without shipping prices included
        :param sale: sale.order recordset
        :return: dict
        """
        result = super()._convert_amount(sale)
        # Remove the shipping amounts for originals amounts
        shipping_amounts = self._convert_shipping(sale).get("amount", {})
        tax = result.get("tax", 0) - shipping_amounts.get("tax", 0)
        untaxed = result.get("untaxed", 0) - shipping_amounts.get("untaxed", 0)
        total = result.get("total", 0) - shipping_amounts.get("total", 0)
        precision = sale.currency_id.decimal_places
        result.update(
            {
                "tax_without_shipping": float_round(tax, precision),
                "untaxed_without_shipping": float_round(untaxed, precision),
                "total_without_shipping": float_round(total, precision),
            }
        )
        return result

    def _prepare_carrier(self, cart, carrier):
        return {
            "id": carrier.id,
            "name": carrier.name,
            "description": carrier.name,
            "price": carrier.rate_shipment(cart).get("price", 0.0),
        }

    def _get_available_carrier(self, cart):
        return [
            self._prepare_carrier(cart, carrier)
            for carrier in cart._get_available_carrier()
        ]

    def _is_item(self, line):
        res = super()._is_item(line)
        return res and not line.is_delivery


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def get_delivery_methods(self):
        """
            This service will return all possible delivery methods for the
            current cart
        :return:
        """
        cart = self._get()
        return self._get_available_carrier(cart)

    def apply_delivery_method(self, **params):
        """
            This service will apply the given delivery method to the current
            cart
        :param params: Dict containing delivery method to apply
        :return:
        """
        cart = self._get()
        if not cart:
            raise UserError(_("There is not cart"))
        else:
            self._set_carrier(cart, params["carrier"]["id"])
            return self._to_json(cart)

    # Validator
    def _validator_apply_delivery_method(self):
        return {
            "carrier": {
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": int,
                        "nullable": True,
                        "required": True,
                        "type": "integer",
                    }
                },
            }
        }

    def _validator_get_delivery_methods(self):
        return {}

    # internal methods
    def _add_item(self, cart, params):
        res = super()._add_item(cart, params)
        self._unset_carrier(cart)
        return res

    def _update_item(self, cart, params, item=False):
        res = super()._update_item(cart, params, item)
        self._unset_carrier(cart)
        return res

    def _delete_item(self, cart, params):
        res = super()._delete_item(cart, params)
        self._unset_carrier(cart)
        return res

    def _set_carrier(self, cart, carrier_id):
        if carrier_id not in [
            x["id"] for x in self._get_available_carrier(cart)
        ]:
            raise UserError(
                _("This delivery method is not available for you order")
            )
        cart.write({"carrier_id": carrier_id})
        cart.get_delivery_price()
        cart.set_delivery_line()

    def _unset_carrier(self, cart):
        cart.write({"carrier_id": False})
        cart._remove_delivery_line()
