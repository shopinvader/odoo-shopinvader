# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.services.helper import secure_params
from openerp.addons.shopinvader.services.cart_item import CartItemService
from openerp.addons.shopinvader.services.cart import CartService
from openerp.addons.shopinvader.backend import shopinvader


@shopinvader(replacing=CartItemService)
class DiscountCartItemService(CartItemService):

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        self._clear_discount()
        return super(DiscountCartItemService, self).create(params)

    @secure_params
    def update(self, params):
        self._clear_discount()
        return super(DiscountCartItemService, self).update(params)

    @secure_params
    def delete(self, params):
        self._clear_discount()
        return super(DiscountCartItemService, self).delete(params)

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _clear_discount(self):
        cart_service = self.service_for(CartService)
        cart = cart_service._get()
        if cart and cart.discount_code:
            cart.discount_code = None
            cart.clear_discount()
