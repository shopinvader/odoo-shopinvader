# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
from io import BytesIO

from PIL import Image, WebPImagePlugin  # noqa: F401

from odoo import api, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = "shopinvader.image.mixin"

    images_webp = Serialized(
        compute="_compute_images",
        string="Shopinvader Image WebP",
        compute_sudo=True,
    )
    images_webp_stored = Serialized()

    def _compute_images(self):
        images_to_recompute = self.filtered(
            lambda x: x._images_must_recompute()
        )
        res = super()._compute_images()
        images_to_recompute._compute_images_webp_stored()
        for record in self:
            record.images_webp = record.images_webp_stored
            # self.images contains the urls with the thumbnails in their
            # original format. To avoid CacheMiss exception we need to
            # assign once again the stored urls to the images field
            record.images = record.images_stored
        return res

    def _compute_images_webp_stored(self):
        for record in self:
            record.images_webp_stored = (
                record._get_image_webp_data_for_record()
            )

    @api.model
    def _create_webp_storage_image(self, image, url_key):
        storage_image_model = self.env["storage.image"].with_context(
            skip_generate_odoo_thumbnail=True
        )
        img = BytesIO(base64.b64decode(image))
        im = Image.open(img).convert("RGB")
        with BytesIO() as output:
            im.save(output, "webp")
            im.close()
            return storage_image_model.create(
                {
                    "name": url_key,
                    "image_medium_url": base64.b64encode(output.getvalue()),
                }
            )

    def _get_image_webp_data_for_record(self):
        res = []
        resizes = self._resize_scales()
        for image_relation in self[self._image_field]:
            url_key = self._get_image_url_key(image_relation) + ".webp"
            webp = self._create_webp_storage_image(
                image_relation.image_id.data, url_key
            )
            image_data = {}
            for resize in resizes:
                thumbnail = webp.get_or_create_thumbnail(
                    resize.size_x, resize.size_y, url_key=url_key
                )
                image_data[resize.key] = self._prepare_data_resize(
                    thumbnail, image_relation
                )
            res.append(image_data)
        return res
