# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def _get_available_payment_mode(self, cart):
        for line in cart.order_line:
            if line.product_id.only_quotation:
                return []
        return super(CartService, self)._get_available_payment_mode(cart)
