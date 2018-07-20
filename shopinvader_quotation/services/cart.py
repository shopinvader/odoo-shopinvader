# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def request_quotation(self, **params):
        cart = self._get()
        if cart.state == 'draft' and cart.typology == 'cart':
            cart.tyopology = 'quotation'
        else:
            raise UserError(_('Impossible to create quotation the order is in the wrong state'))
        return self._to_json(cart)
