# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.http import route


class TransactionShopinvaderController(InvaderController):

    @route('/shopinvader/cart/check_payment/<string:provider_name>',
           methods=['GET'], auth="shopinvader")
    def check_payment(self, **params):
        return self._process_method('cart', 'check_payment', params=params)
