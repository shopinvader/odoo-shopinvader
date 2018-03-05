# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderImageMixin(models.AbstractModel):
    _name = 'shopinvader.image.mixin'

    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')

    def _compute_image(self):
        for record in self:
            record.images = record._get_images_for_record()

    def _get_odoo_image_url(self, base_url):
        return base_url + '/web/image/%s/%s/image' % (self._name, self.id)

    def _get_images_for_record(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo()\
            .get_param('web.base.url')
        image_url = self._get_odoo_image_url(base_url)
        res = {
            'original': {
                'src': image_url,
                'alt': self.name,
            }
        }
        resizes = self.backend_id[
            '%s_resize_ids' % self._name.replace('.', '_')]
        for resize in resizes:
            res[resize.key] = {
                'src': image_url + '/%sx%s' % (resize.size_x, resize.size_y),
                'alt': self.name,
                }
        return [res]
