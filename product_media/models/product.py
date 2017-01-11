# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductMediaLink(models.Model):
    _name = 'product.media.link'
    _description = 'Product Media Link'

    product_tmpl_id = fields.Many2one(
        'product.template',
        'Product Tmpl')
    restrict_variant_ids = fields.Many2many(
        comodel_name='product.product',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        string='Restrict Variant')
    media_ids = fields.Many2many(
        comodel_name='ir.attachment.media',
        string='Media')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    media_link_ids = fields.One2many(
        'product.media.link',
        'product_tmpl_id',
        string='Media')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    media_ids = fields.Many2many(
        comodel_name='ir.attachment.media',
        string='Media',
        compute='_compute_media')

    def _compute_media(self):
        for record in self:
            links = self.env['product.media.link'].search([
                '|',
                ('restrict_variant_ids', '=', False),
                ('restrict_variant_ids', '=', record.id),
                ('product_tmpl_id', '=', record.product_tmpl_id.id),
                ])
            record.media_ids = links.mapped('media_ids')
