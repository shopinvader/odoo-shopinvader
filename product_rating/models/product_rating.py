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
    partner_name = fields.Char(required=True)
    state = fields.Selection([
        ('appproved', 'Appproved'),
        ('pending', 'Pending'),
        ('refused', 'Refused'),
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
    rating = fields.Integer(compute='_compute_rating', group_operator='avg')
    select_rating = fieldname = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ])

    def _compute_rating(self):
        for record in self:
            record.rating = float(record.select_rating)

    @api.multi
    def approve(self):
        return self.write({'state': 'approved'})

    @api.multi
    def refuse(self):
        return self.write({'state': 'refused'})

    @api.onchange('partner_id')
    def change_partner(self):
        self.partner_name = self.partner_id.name
