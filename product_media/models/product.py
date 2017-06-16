# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from openerp import api, fields, models
import logging
_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError, err:
    _logger.debug(err)


class ProductMediaType(models.Model):
    _name = 'product.media.type'
    _description = 'Product Media Type'

    name = fields.Char(translated=True)
    code = fields.Char()


class ProductMedia(models.Model):
    _name = 'product.media'
    _description = 'Product Media'
    _inherits = {'storage.file': 'file_id'}

    restrict_variant_ids = fields.Many2many(
        comodel_name='product.product',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        string='Restrict Variant')

    media_type_id = fields.Many2one(
        'product.media.type',
        'Media Type')

    def read(self, cr, uid, ids,
             fields=None, context=None, load='_classic_read'):
        # Hack for binary compatibility
        add_datas_size = False
        if context.get('bin_size') and 'datas' in fields:
            fields.remove('datas')
            fields.append('human_file_size')
            add_datas_size = True
        res = super(ProductMedia, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if add_datas_size:
            for record in res:
                record['datas'] = record['human_file_size']
        return res

    @api.onchange('name')
    def onchange_name(self):
        for record in self:
            if record.name:
                filename, extension = os.path.splitext(record.name)
                record.name = "%s%s" % (slugify(filename), extension)

    @api.model
    def default_get(self, fields_list):
        res = super(ProductMedia, self).default_get(fields_list)
        if 'backend_id' in fields_list:
            res['backend_id'] = self._deduce_backend_id()
        if 'res_model' in fields_list:
            res['res_model'] = 'product.template'
        return res

    def _deduce_backend_id(self):
        """Choose the correct backend.

        By default : it's the one configured as ir.config_parameter
        Overload this method if you need something more powerfull
        """
        return int(self.env['ir.config_parameter'].get_param(
            'storage.media.backend_id'))

    @api.model
    def create(self, vals):
        # ORM bug computed field are not visible
        # in write from the inherited class
        # so it's drop need to set it manuallly
        datas = vals.pop('datas')
        media = super(ProductMedia, self).create(vals)
        media.file_id.datas = datas
        return media


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    media_ids = fields.One2many(
        comodel_name='product.media',
        inverse_name='res_id',
        string='Media',
        domain=lambda self: [("res_model", "=", self._name)],
        copy=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    media_ids = fields.Many2many(
        comodel_name='product.media',
        string='Media',
        compute='_compute_media')

    def _compute_media(self):
        for record in self:
            record.media_ids = self.env['product.media'].search([
                '|',
                ('restrict_variant_ids', '=', False),
                ('restrict_variant_ids', '=', record.id),
                ('res_id', '=', record.product_tmpl_id.id),
                ])
