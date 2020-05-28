# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def set_carrier(self, **params):
        """
           This service will set the given delivery method to the current
           cart
       :param params: The carrier_id to set
       :return:
       """
        cart = self._get()
        if not cart:
            raise UserError(_("There is not cart"))
        else:
            self._set_carrier(cart, params["carrier_id"])
            return self._to_json(cart)

    # DEPRECATED METHODS #
    def get_delivery_methods(self):
        """
            !!!!DEPRECATED!!!!! Uses delivery_carrier.search

            This service will return all possible delivery methods for the
            current cart

        :return:
        """
        _logger.warning(
            "DEPRECATED: You should use %s in service %s",
            "search",
            "delivery_carrier",
        )
        return self.component("delivery_carrier").search(
            target="current_cart"
        )["rows"]

    def apply_delivery_method(self, **params):
        """
            !!!!DEPRECATED!!!!! Uses set_carrier

            This service will apply the given delivery method to the current
            cart
        :param params: Dict containing delivery method to apply
        :return:
        """
        return self.set_carrier(carrier_id=params["carrier"]["id"])

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
        return {
            "country_id": {
                "coerce": to_int,
                "required": False,
                "type": "integer",
            },
            "zip_code": {"required": False, "type": "string"},
        }

    def _validator_set_carrier(self):
        return {
            "carrier_id": {
                "coerce": int,
                "nullable": True,
                "required": True,
                "type": "integer",
            }
        }

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
            x["id"] for x in cart._invader_available_carriers()
        ]:
            raise UserError(
                _("This delivery method is not available for you order")
            )
        cart._set_carrier_and_price(carrier_id)

    def _unset_carrier(self, cart):
        cart.write({"carrier_id": False})
        cart._remove_delivery_line()

    def _get_lines_to_copy(self, cart):
        """
        Don't copy delivery lines
        :param cart:
        :return:
        """
        res = super(CartService, self)._get_lines_to_copy(cart)
        return res.filtered(lambda l: not l.is_delivery)
