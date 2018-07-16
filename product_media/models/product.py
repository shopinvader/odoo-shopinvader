# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError, err:
    _logger.debug(err)


class ProductMediaType(models.Model):
    """Define new object to add feature of Product Media Type."""

    _name = 'product.media.type'
    _description = 'Product Media Type'

    name = fields.Char(translated=True)
    code = fields.Char()


class ProductMedia(models.Model):
    """Define new object to add Product's Media."""

    _name = 'product.media'
    _description = 'Product Media'
    _inherits = {'storage.file': 'file_id'}

    file_id = fields.Many2one(
        'storage.file',
        'File',
        required=True,
        ondelete='cascade')
    restrict_variant_ids = fields.Many2many('product.product',
                                            string='Restrict Variant')

    media_type_id = fields.Many2one(
        'product.media.type',
        'Media Type')
    res_id = fields.Many2one('product.template', 'Product Template')

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """Override this method to resize the data file."""
        # Hack for binary compatibility
        add_datas_size = False
        context = self.env.context
        if context.get('bin_size') and 'data' in fields:
            fields.remove('data')
            fields.append('human_file_size')
            add_datas_size = True
        res = super(ProductMedia, self).read(fields=fields, load=load)
        if add_datas_size:
            for record in res:
                record['data'] = record['human_file_size']
        return res

    @api.onchange('name')
    def onchange_name(self):
        """The method to set file name with extension if change name."""
        if self.name:
            filename, extension = os.path.splitext(self.name)
            self.name = "%s%s" % (slugify(filename), extension)

    @api.model
    def default_get(self, fields_list):
        """The method used to set default value of backend_id and res_model."""
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
        """Override the method to set file."""
        # ORM bug computed field are not visible
        # in write from the inherited class
        # so it's drop need to set it manuallly
        datas = False
        if vals.get('data'):
            datas = vals.pop('data')
        media = super(ProductMedia, self).create(vals)
        media.file_id.data = datas
        return media


class ProductTemplate(models.Model):
    """Enhance the object to add media feature."""

    _inherit = 'product.template'

    media_ids = fields.One2many('product.media', 'res_id',
                                string='Media',
                                copy=True)


class ProductProduct(models.Model):
    """Enhance the object to add media feature."""

    _inherit = 'product.product'

    variant_media_ids = fields.Many2many('product.media',
                                         string='Media',
                                         compute='_compute_media')

    def _compute_media(self):
        for record in self:
            record.variant_media_ids = self.env['product.media'].search([
                '|',
                ('restrict_variant_ids', '=', False),
                ('restrict_variant_ids', '=', record.id),
                ('res_id', '=', record.product_tmpl_id.id),
            ])
