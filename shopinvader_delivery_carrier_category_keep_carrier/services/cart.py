# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class CartService(Component):

    _inherit = "shopinvader.cart.service"

    def _check_carrier_unset(self, cart, params):
        """
        The carrier category does not need to unset
        :param cart:
        :param params:
        :return:
        """
        if cart.carrier_id.category_id.keep_carrier_on_shipping_change:
            return False
        return super(CartService, self)._check_carrier_unset(cart, params)
