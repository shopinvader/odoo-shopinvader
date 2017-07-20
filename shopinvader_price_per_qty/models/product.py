# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    def _get_price(self, pricelist, fposition):
        vals = super(ShopinvaderVariant, self)._get_price(pricelist, fposition)
        items = self.env['product.pricelist.item'].search([
            '|', '|', '|',
            ('product_id', '=', self.record_id.id),
            ('product_tmpl_id', '=', self.product_tmpl_id.id),
            ('categ_id', '=', self.categ_id.id),
            '&', '&',
            ('product_id', '=', False),
            ('categ_id', '=', False),
            ('product_tmpl_id', '=', False),
            ])
        item_qty = set([item.min_quantity
                        for item in items if item.min_quantity > 1])
        vals['price_per_qty'] = {}
        for qty in item_qty:
            if qty == 1:
                continue
            vals['price_per_qty'][qty] = self._get_price_per_qty(
                qty, pricelist, fposition)['value']
        return vals
