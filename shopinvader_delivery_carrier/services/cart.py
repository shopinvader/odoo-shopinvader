# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


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
