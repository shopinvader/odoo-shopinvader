# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.services.helper import secure_params
from openerp.addons.shopinvader.services.cart import CartService
from openerp.addons.shopinvader.backend import shopinvader
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


@shopinvader(replacing=CartService)
class DiscountCartService(CartService):

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def update(self, params):
        coupon_code = params.pop('coupon_code', None)
        res = super(DiscountCartService, self).update(params)
        if coupon_code is not None:
            if 'payment_params' in params:
                raise UserError(
                    _("Appling discount and paying can "
                      "not be done in the same call"))
            cart = self._get()
            if coupon_code:
                cart.add_coupon(coupon_code)
            else:
                cart.promotion_rule_id = None
                cart.clear_promotion_line()
            return self._to_json(cart)
        return res

    # Validator
    def _validator_update(self):
        res = super(DiscountCartService, self)._validator_update()
        res['coupon_code'] = {'type': 'string'}
        return res

    def _parser(self):
        res = super(DiscountCartService, self)._parser()
        res.append(
            ('promotion_rule_id:promotion_rule',
                ['name', 'code', 'discount_amount', 'rule_type:type']))
        return res

    def _parser_order_line(self):
        parser = super(DiscountCartService, self)._parser_order_line()
        parser.append(
            ('promotion_rule_id:promotion_rule',
                ['name', 'code', 'discount_amount', 'rule_type:type']))
        return parser
