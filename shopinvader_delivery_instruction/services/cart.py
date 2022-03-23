# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _validator_update(self):
        """
        Inherit to add the delivery_instruction validator
        :return: dict
        """
        validator = super()._validator_update()
        validator.update({"delivery_instruction": {"type": "string"}})
        return validator

    def _prepare_delivery_instruction(self, delivery_instruction, params):
        """
        Put the given delivery note into params dict (used to create the
        sale.order).
        :param delivery_instruction: str or bool
        :param params: dict
        :return: bool
        """
        # If the user try to remove the value, we'll have an empty string
        if delivery_instruction or isinstance(delivery_instruction, str):
            params.update({"picking_note": delivery_instruction})
        return True

    def _prepare_update(self, cart, params):
        """
        Inherit to add the picking note into the cart
        :param cart: sale.order recordset
        :param params: dict
        :return: dict
        """
        params = super()._prepare_update(cart, params)
        self._prepare_delivery_instruction(
            params.pop("delivery_instruction", False), params
        )
        return params
