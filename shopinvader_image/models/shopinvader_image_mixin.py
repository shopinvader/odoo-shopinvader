# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderImageMixin(models.AbstractModel):
    _name = 'shopinvader.image.mixin'
    _image_field = None

    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')

    def _compute_image(self):
        # Note: this computed field depend on the lang used in the context
        # as the name of the record is used for generating the thumbnail
        for record in self:
            record.images = record._get_image_data_for_record()

    def _get_image_url_key(self, image_relation):
        # You can inherit this method to change the name of the image of
        # your website. By default we use the name of the product or category
        # linked to the image processed
        # Note the url will be slugify by the get_or_create_thumnail
        return self.display_name

    def _get_image_data_for_record(self):
        self.ensure_one()
        res = []
        resizes = self.backend_id[
            '%s_resize_ids' % self._name.replace('.', '_')]
        for image_relation in self[self._image_field]:
            url_key = self._get_image_url_key(image_relation)
            image_data = {}
            tag = ''
            if image_relation.tag_id:
                tag = image_relation.tag_id.name
            for resize in resizes:
                thumbnail = image_relation.image_id.get_or_create_thumbnail(
                    resize.size_x,
                    resize.size_y,
                    url_key=url_key)
                image_data[resize.key] = {
                    'src': thumbnail.url,
                    'alt': self.name,
                    'tag': tag,
                    }
            res.append(image_data)
        return res
