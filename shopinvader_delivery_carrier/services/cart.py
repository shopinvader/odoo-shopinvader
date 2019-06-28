# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def get_delivery_methods(self, **params):
        """
        This service will return all possible delivery methods for the
        current cart (depending on country/zip)
        The cart is not updated with the given country/zip. The change is done
        only in memory.
        :param params: dict
        :return: dict
        """
        cart = self._get()
        country = self._load_country(params)
        zip_code = self._load_zip_code(params)
        if country or zip_code:
            cart = cart.with_context(
                delivery_force_country_id=country.id,
                delivery_force_zip_code=zip_code,
            )
        result = self._get_available_carrier(cart)
        return result

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
        return {
            "country_id": {
                "coerce": to_int,
                "required": False,
                "type": "integer",
            },
            "zip_code": {"required": False, "type": "string"},
        }

    # internal methods
    def _load_country(self, params):
        """
        Load the country from given params
        :param params: dict
        :return: res.country recordset
        """
        country_id = params.pop("country_id", 0)
        return self.env["res.country"].browse(country_id)

    def _load_zip_code(self, params):
        """
        Load the country from given params
        :param params: dict
        :return: str
        """
        return params.pop("zip_code", "")

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
