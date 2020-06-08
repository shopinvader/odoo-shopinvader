# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited,method-required-super

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class DeliveryCarrierService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.delivery.carrier.service"
    _usage = "delivery_carriers"
    _description = """
        This service allows you to retrieve the informations of available
        delivery carriers.
    """

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
        delivery_carriers = self._search(**params)
        vals = {
            "size": len(delivery_carriers),
            "data": [self._prepare_carrier(dc) for dc in delivery_carriers],
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

    def _search(self, **params):
        """
        Search for delivery carriers
        :param params: see _validator_search
        :return: delivery.carriers recordset
        """
        if params.get("target") == "current_cart":
            cart = self.component(usage="cart")._get()
            country = self._load_country(params)
            zip_code = self._load_zip_code(params)
            if country or zip_code:
                cart = cart.with_context(
                    delivery_force_country_id=country.id,
                    delivery_force_zip_code=zip_code,
                )
            return cart._get_available_carrier()
        return self.shopinvader_backend.carrier_ids

    def _prepare_carrier(self, carrier, no_price=False):
        res = carrier.jsonify(self._json_parser_carrier(no_price=no_price))[0]
        res["type"] = None
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

    def _json_parser_carrier(self, no_price=False):
        res = ["id", "name", "default_code:code", "description"]
        if not no_price:
            res.append("price")
        return res


class DeprecatedDeliveryCarrierService(Component):
    _inherit = "shopinvader.delivery.carrier.service"
    _name = "shopinvader.deprecated.delivery.carrier.service"
    _usage = "delivery_carrier"
    _description = "Deprecated use 'delivery_carriers' instead"
