# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class RatingMixing(models.AbstractModel):
    """New object to calculate product rating."""

    _name = 'rating.mixing'

    rating = fields.Float(
        compute='_compute_rating',
        group_operator='avg',
        digits=dp.get_precision('Product Rating'),
        store=True)

    def _compute_rating(self):
        key = self._fields['rating_ids']._description_relation_field
        res = self.env['product.rating'].read_group([
            (key, 'in', self.ids),
            ('state', '=', 'approved'),
        ], ['rating', key], [key])
        res = {x[key][0]: x['rating'] for x in res}
        for record in self:
            record.rating = res.get(record.id, 0)


class ProductTemplate(models.Model):
    """Enahance the module to add rating feature."""

    _inherit = ['product.template', 'rating.mixing']
    _name = 'product.template'

    rating_ids = fields.One2many(
        'product.rating',
        'product_tmpl_id',
        'Rating')

    @api.depends('rating_ids.rating', 'rating_ids.state')
    def _compute_rating(self):
        super(ProductTemplate, self)._compute_rating()


class ProductProduct(models.Model):
    """Enahance the module to add rating feature."""

    _inherit = ['product.product', 'rating.mixing']
    _name = 'product.product'

    rating_ids = fields.One2many(
        'product.rating',
        'product_id',
        'Rating')

    @api.depends('rating_ids.rating', 'rating_ids.state')
    def _compute_rating(self):
        super(ProductProduct, self)._compute_rating()
