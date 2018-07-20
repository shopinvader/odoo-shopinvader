# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = [
        'shopinvader.cart.service',
        'shopinvader.abstract.payment.service'
    ]
    _name = 'shopinvader.cart.service'
