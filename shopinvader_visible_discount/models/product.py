# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    def _extract_price_from_onchange(self, pricelist, onchange_vals):
        vals = super(ShopinvaderVariant, self)._extract_price_from_onchange(
            pricelist, onchange_vals)
        prec = self.env['decimal.precision'].precision_get('Product')
        discount = round(onchange_vals['value'].get('discount', 0), prec)
        if discount:
            new_price = round(vals['value'] * (1-discount/100), prec)
            vals.update({
                'value': new_price,
                'discount': discount,
                'original_value': vals['value']
                })
        return vals
