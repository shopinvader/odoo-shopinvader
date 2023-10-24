# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def check_exceptions(self, **params):
        """Run sale exception checks"""
        cart = self._get(create_if_not_found=False)
        if not cart:
            return {}
        cart.detect_exceptions()
        return cart.exception_ids.jsonify(self._parser_exception())

    def _validator_check_exceptions(self):
        return {}

    def _parser_exception(self):
        return ["name", "description"]

    def _convert_one_sale(self, cart):
        res = super()._convert_one_sale(cart)
        res["sale_exceptions"] = cart.exception_ids.jsonify(self._parser_exception())
        return res
