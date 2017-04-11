# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductRating(models.Model):
    _name = 'product.rating'
    _description = 'Product Rating'

    name = fields.Char(required=True)
    comment = fields.Text(required=True)
    nickname = fields.Char(required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('refused', 'Refused'),
        ('approved', 'Approved'),
        ], default='pending',
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner')
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        'Product Tmpl',
        related='product_id.product_tmpl_id',
        store=True)
    rating = fields.Float(
        compute='_compute_rating',
        group_operator='avg',
        store=True)
    select_rating = fieldname = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ])

    @api.depends('select_rating')
    def _compute_rating(self):
        for record in self:
            record.rating = float(record.select_rating)

    @api.onchange('partner_id')
    def change_partner(self):
        self.nickname = self.partner_id.name
