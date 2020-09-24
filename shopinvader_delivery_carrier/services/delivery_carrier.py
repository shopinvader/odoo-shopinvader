# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited,method-required-super

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class DeliveryCarrierService(Component):
    """Shopinvader service to retrieve delivery carrier information.
    """

    _inherit = "base.shopinvader.service"
    _name = "shopinvader.delivery.carrier.service"
    _usage = "delivery_carrier"
    _description = __doc__

    # Public services:

    def search(self, **params):
        """
        Returns the list of available carriers

        If the target params == current_cart, the list will be limited to the
        carriers applying to the current cart and a price will be filled
        into the response otherwise the price is not relevant (always 0).

        The field type is a technical field only use inform if the carrier
        provides some specialized functionalities
        """
        cart = None
        if params.get("target") == "current_cart":
            cart = self.component(usage="cart")._get()
        delivery_carriers = self._search(cart=cart, **params)
        vals = {
            "size": len(delivery_carriers),
            "data": [
                self._prepare_carrier(dc, cart) for dc in delivery_carriers
            ],
        }
        # TODO DEPRECATED this old API is deprecated
        #  keep returing the result but this should be not used anymore
        vals.update({"count": vals["size"], "rows": vals["data"]})
        return vals

    # Validators

    def _validator_search(self):
        return {
            "target": {
                "type": "string",
                "required": False,
                "allowed": ["current_cart"],
            },
            "country_id": {
                "coerce": to_int,
                "required": False,
                "type": "integer",
            },
            "zip_code": {"required": False, "type": "string"},
        }

    def _validator_return_search(self):
        schema = {
            "size": {"type": "integer", "required": True},
            "data": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "name": {
                            "type": "string",
                            "required": False,
                            "nullable": True,
                        },
                        "code": {
                            "type": "string",
                            "required": False,
                            "nullable": True,
                        },
                        "description": {
                            "type": "string",
                            "required": False,
                            "nullable": True,
                        },
                        "price": {"type": "float", "required": False},
                        "type": {
                            "type": "string",
                            "required": False,
                            "allowed": self.allowed_carrier_types,
                            "nullable": True,
                        },
                    },
                },
            },
        }
        # TODO DEPRECATED this old API is deprecated
        schema.update({"count": schema["size"], "rows": schema["data"]})
        return schema

    # Services implementation

    def _search(self, cart, **params):
        """
        Search for delivery carriers
        :param: cart: if provided, the list will be limited to the carrier
          applying to the given cart
        :param params: see _validator_search
        :return: delivery.carriers recordset
        """
        if cart:
            country = self._load_country(params)
            zip_code = self._load_zip_code(params)
            if country or zip_code:
                cart = cart.with_context(
                    delivery_force_country_id=country.id,
                    delivery_force_zip_code=zip_code,
                )
            return cart._invader_available_carriers()
        return self.shopinvader_backend.carrier_ids

    def _prepare_carrier(self, carrier, cart=None):
        res = carrier.jsonify(self._json_parser_carrier, one=True)
        res["type"] = None
        price = 0.0
        if cart:
            price = carrier.rate_shipment(cart).get("price", 0.0)
        res["price"] = price
        return res

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

    @property
    def allowed_carrier_types(self):
        return []

    @property
    def _json_parser_carrier(self):
        return ["id", "name", "code", "description"]
