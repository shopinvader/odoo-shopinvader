# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.controllers.main import ShopinvaderController
from odoo.http import route


class TransactionShopinvaderController(ShopinvaderController):

    # Check Transaction
    @route('/shopinvader/check_transaction',
           methods=['GET'], auth="shopinvader")
    def check_transaction(self, **params):
        return self.send_to_service('transaction.service', params)


