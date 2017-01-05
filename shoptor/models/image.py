# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class Image(models.Model):
    _inherit = 'base_multi_image.image'

    locomotivecms_bind_ids = fields.One2many(
        'locomotivecms.image',
        'record_id',
        string='Locomotive Binding')

    #Automatically create the locomotive binding for the image created
    @api.model
    def create(self, vals):
        image = super(ProductImage, self).create(vals)
	if image.owner_model == 'product.template':
            product = self.env['product.template'].browse(image.owner_id)
            for binding in product.locomotivecms_bind_ids:
                self.env['locomotive.image'].create({
                    'record_id': image.id,
                    'backend_id': binding.backend_id.id,
                    })
        return image


class LocomotivecmsImage(models.Model):
    _name = 'locomotivecms.image'
    _inherit = 'locomotivecms.binding'
    _inherits = {'base_multi_image.image': 'record_id'}

    record_id = fields.Many2one(
        'base_multi_image.image',
        required=True,
        ondelete='cascade')
    url = fields.Char()
    size = fields.Selection([
        ('full', 'full'),
        ('300x250', '300x250'),
        ])
