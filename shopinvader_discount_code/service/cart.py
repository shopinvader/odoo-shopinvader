# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.services.helper import secure_params
from openerp.addons.shopinvader.services.cart import CartService
from openerp.addons.shopinvader.backend import shopinvader


@shopinvader
class DiscountService(CartService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def update(self, params):
        res = super(DiscountService, self).update(params)
        if params.get('discount_code'):
            cart = self._get()
            cart.apply_discount()
        return res

    # Validator
    def _validator_update(self):
        res = super(DiscountService, self)._validator_update()
        res['discount_code'] = {'type': 'string'}
        return res

    def _parser(self):
        res = super(DiscountService, self)._parser()
        res.append('discount_code')
        return res
