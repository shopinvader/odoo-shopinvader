# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug('Cannot `import slugify`.')


class ShopinvaderVariantJsonImageExport(Component):
    _name = 'shopinvader.variant.json.image.export'
    _inherit = 'json.export.mapper'
    _apply_on = ['shopinvader.variant']
    _collection = 'se.backend.algolia'

    def _get_image_json(self, shopinvader_variant):
        """

        :param shopinvader_variant: shopinvader.variant
        :return: dict/json
        """
        # Todo; tocheck: already into the right index/lang?
        backend = shopinvader_variant.backend_id
        json_images = {}
        thumbnail_obj = self.env['storage.image']
        for image_resize in backend.shopinvader_variant_resize_ids:
            # get thumbnail image
            url_key = slugify(shopinvader_variant.display_name)
            size_x = image_resize.size_x
            size_y = image_resize.size_y
            thumbnail = thumbnail_obj.get_or_create_thumbnail(
                size_x, size_y, url_key=url_key)
            sub_json_image = {
                'src': thumbnail.image_medium_url,
                'alt': shopinvader_variant.display_name,
            }
            json_images.update({
                image_resize.name: sub_json_image,
            })
        return json_images

    def _apply(self, map_record, options=None):
        """
        Inherit the function to add json image data/path
        :param map_record: shopinvader.variant
        :param options: dict
        :return: dict/json
        """
        values = self._get_image_json(map_record.source)
        values.update(super(ShopinvaderVariantJsonImageExport, self)._apply(
            map_record=map_record, options=options))
        return values
