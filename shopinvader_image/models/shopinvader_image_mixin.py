# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderImageMixin(models.AbstractModel):
    _name = "shopinvader.image.mixin"
    _description = "Shopinvader Image Mixin"
    _image_field = None

    images = Serialized(
        compute="_compute_images",
        string="Shopinvader Image",
        compute_sudo=True,
    )
    # Tech field to store images data.
    # It cannot be computed because the computation
    # might required generating thumbs
    # which requires access to the storage files
    # which requires components registry to be available
    # which is not the case when Odoo starts.
    images_stored = Serialized()
    images_store_hash = fields.Char()

    def _compute_images(self):
        # Force computation if needed
        self.filtered(lambda x: x._images_must_recompute())._compute_images_stored()
        for record in self:
            record.images = record.images_stored

    def _compute_images_stored(self):
        for record in self:
            record.images_stored = record._get_image_data_for_record()
            record.images_store_hash = record._get_images_store_hash()

    def _images_must_recompute(self):
        return self.images_store_hash != self._get_images_store_hash()

    @property
    def _resize_scales_field(self):
        return "%s_resize_ids" % self._name.replace(".", "_")

    def _resize_scales(self):
        return self.backend_id[self._resize_scales_field]

    def _get_images_store_hash(self):
        return str(hash(self._get_images_store_hash_tuple()))

    def _get_images_store_hash_tuple(self):
        images = self[self._image_field].image_id
        # Get fresh URLs.
        # Normally we have only one backend
        # but potentially you can have different backends by image record.
        # If any base URL changes, images should be recomputed.
        # Eg: swap an image to another backend or change the CDN URL.
        # NOTE: this is not perfect in terms of perf because it will cause
        # calls to `get_or_create_thumbnail` when no image data has changed
        # but it's better than having broken URLs.
        public_urls = tuple(images.mapped("url"))
        resize_scales = tuple(
            self._resize_scales().mapped(lambda r: (r.key, r.size_x, r.size_y))
        )
        images_timestamp = tuple(images.mapped("write_date"))
        # TODO: any other bit to consider here?
        return resize_scales + images_timestamp + public_urls

    def _get_image_url_key(self, image_relation):
        # You can inherit this method to change the name of the image of
        # your website. By default we use the name of the product or category
        # linked to the image processed
        # Note the url will be slugify by the get_or_create_thumnail
        self.ensure_one()
        return self.display_name

    def _get_image_data_for_record(self):
        self.ensure_one()
        res = []
        resizes = self._resize_scales()
        for image_relation in self[self._image_field]:
            url_key = self._get_image_url_key(image_relation)
            image_data = {}
            for resize in resizes:
                thumbnail = image_relation.image_id.get_or_create_thumbnail(
                    resize.size_x, resize.size_y, url_key=url_key
                )
                image_data[resize.key] = self._prepare_data_resize(
                    thumbnail, image_relation
                )
            res.append(image_data)
        return res

    def _prepare_data_resize(self, thumbnail, image_relation):
        """
        Prepare data to fill images serialized field
        :param thumbnail: storage.thumbnail recordset
        :param image_relation: product.image.relation recordset
        :return: dict
        """
        self.ensure_one()
        tag = ""
        if image_relation.tag_id:
            tag = image_relation.tag_id.name
        return {"src": thumbnail.url, "alt": self.name, "tag": tag}
