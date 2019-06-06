# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.base_url.models.abstract_url import get_model_ref


class ShopinvaderCategory(models.Model):
    _name = "shopinvader.category"
    _description = "Shopinvader Category"
    _inherit = ["shopinvader.binding", "abstract.url", "seo.title.mixin"]
    _inherits = {"product.category": "record_id"}
    _order = "sequence"

    record_id = fields.Many2one(
        "product.category", required=True, ondelete="cascade", index=True
    )
    object_id = fields.Integer(
        compute="_compute_object_id", store=True, index=True
    )
    sequence = fields.Integer()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    subtitle = fields.Char()
    short_description = fields.Html()
    description = fields.Html()
    shopinvader_parent_id = fields.Many2one(
        "shopinvader.category",
        "Shopinvader Parent",
        compute="_compute_parent_category",
        store=True,
        index=True,
        compute_sudo=True,
    )
    shopinvader_child_ids = fields.One2many(
        "shopinvader.category", inverse_name="shopinvader_parent_id"
    )
    level = fields.Integer(compute="_compute_level")
    redirect_url_key = fields.Serialized(
        compute="_compute_redirect_url_key", string="Redirect Url Keys"
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "record_uniq",
            "unique(backend_id, record_id, lang_id)",
            "A category can only have one binding by backend.",
        )
    ]

    @api.multi
    def name_get(self):
        return [(cat.id, cat.record_id.display_name) for cat in self]

    def _compute_redirect_url_key(self):
        for record in self:
            res = []
            for url in record.redirect_url_url_ids:
                res.append(url.url_key)
            record.redirect_url_key = res

    @api.depends("record_id")
    def _compute_object_id(self):
        for record in self:
            record.object_id = record.record_id.id

    @api.depends(
        "parent_id.shopinvader_bind_ids.shopinvader_parent_id",
        "shopinvader_parent_id.active",
    )
    def _compute_parent_category(self):
        for record in self:
            for binding in record.parent_id.shopinvader_bind_ids:
                if (
                    binding.backend_id == record.backend_id
                    and binding.lang_id == record.lang_id
                    and binding.active
                ):
                    record.shopinvader_parent_id = binding
                    break

    def _post_process_url_key(self, key):
        key = super(ShopinvaderCategory, self)._post_process_url_key(key)
        if self.parent_id and self.shopinvader_parent_id.active:
            if not self.shopinvader_parent_id.automatic_url_key:
                self.shopinvader_parent_id._compute_automatic_url_key()
            parent_url = self.shopinvader_parent_id.automatic_url_key
            key = "/".join([parent_url, key])
        return key

    @api.multi
    @api.depends(
        "lang_id", "record_id.name", "shopinvader_parent_id.automatic_url_key"
    )
    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()

    @api.depends(
        "shopinvader_parent_id",
        "shopinvader_parent_id.level",
        "shopinvader_parent_id.active",
    )
    def _compute_level(self):
        for record in self:
            record.level = 0
            parent = record.shopinvader_parent_id
            while parent and parent.active:
                record.level += 1
                parent = parent.shopinvader_parent_id

    def _unbind(self):
        shopinvader_child_cat = self.browse()
        for shopinvader_cat in self:
            categ_id = shopinvader_cat.record_id
            childs_cat = self.env["product.category"].search(
                [("id", "child_of", categ_id.id)]
            )
            shopinvader_child_cat = self.search(
                [
                    ("record_id", "in", childs_cat.ids),
                    ("backend_id", "=", shopinvader_cat.backend_id.id),
                ]
            )
        categories = self | shopinvader_child_cat
        categories.write({"active": False})

    def _redirect_existing_url(self):
        for record in self.filtered(lambda c: c.url_url_ids):
            categ = record.shopinvader_parent_id
            if categ:
                record.url_url_ids.write(
                    {"redirect": True, "model_id": get_model_ref(categ)}
                )
        return True
