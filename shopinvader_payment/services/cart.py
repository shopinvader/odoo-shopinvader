# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = [
        'shopinvader.abstract.payment.service',
        'shopinvader.cart.service',
    ]
    _name = 'shopinvader.cart.service'

    def _load_target(self, params):
        """

        :param params: dict
        :return: exposed model recordset
        """
        return self._get()

    def _action_after_payment(self, target):
        """
        Confirm the cart after the payment
        :param target: payment recordset
        :return: dict
        """
        values = super(CartService, self)._action_after_payment(target)
        values.update(self._confirm_cart(target))
        return values
