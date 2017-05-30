# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    rating = fields.Serialized(
        compute='_compute_rating',
        string='Rating')

    def _compute_rating(self):
        for record in self:
            reviews = []
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in record.rating_ids:
                if rating.state == 'approved':
                    reviews.append({
                        'nickname': rating.nickname,
                        'name': rating.name,
                        'comment': rating.comment,
                        'rating': rating.rating,
                        'product_code': rating.product_id.default_code,
                        })
                    distribution[rating.rating] += 1
            if reviews:
                count = len(reviews)
                average = sum([c['rating'] for c in reviews]) / count
                record.rating = {
                    'reviews': reviews,
                    'summary': {
                        'average': average,
                        'count': count,
                        'distribution': distribution,
                        }}
            else:
                record.rating = {}
