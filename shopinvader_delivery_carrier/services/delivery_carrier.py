# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited,method-required-super

from openerp.addons.component.core import Component


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
        return {
            "count": len(delivery_carriers),
            "rows": [self._prepare_carrier(dc) for dc in delivery_carriers],
        }

    # Validators

    def _validator_search(self):
        return {
            "target": {
                "type": "string",
                "required": False,
                "allowed": ["current_cart"],
            }
        }

    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
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

    # Services implementation

    def _search(self, **params):
        """
        Search for delively carriers
        :param params: see _validator_search
        :return: a list of delivery.carriers
        """
        if params.get("target") == "current_cart":
            return self.component(usage="cart")._get()._get_available_carrier()
        return self.shopinvader_backend.carrier_ids

    def _prepare_carrier(self, carrier):
        res = carrier.jsonify(self._json_parser_carrier)[0]
        res["type"] = None
        return res

    @property
    def allowed_carrier_types(self):
        return []

    @property
    def _json_parser_carrier(self):
        return ["id", "name", "description", "price"]
