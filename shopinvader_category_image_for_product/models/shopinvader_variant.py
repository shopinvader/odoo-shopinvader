# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.fields import first


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _inherit = ["shopinvader.variant"]

    image_categories = fields.Serialized(compute="_compute_image_categories")

    @api.model
    def _get_category_by_backend(self, record):
        return record.shopinvader_categ_ids.filtered(
            lambda c, v=record: c.record_id == v.categ_id
            and c.index_id.backend_id == v.index_id.backend_id
            and c.images
        )

    @api.multi
    @api.depends(
        "shopinvader_categ_ids",
        "shopinvader_categ_ids.index_id",
        "shopinvader_categ_ids.index_id.backend_id",
        "shopinvader_categ_ids.images",
    )
    def _compute_image_categories(self):
        """
        Compute function for image_categories field.
        This field should contains the value of images field into the first
        category found (with same backend)
        :return:
        """
        for record in self:
            category = self._get_category_by_backend(record)
            record.image_categories = first(category).images or []
