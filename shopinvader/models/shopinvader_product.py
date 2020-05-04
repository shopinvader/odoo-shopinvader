# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderProduct(models.Model):
    _name = "shopinvader.product"
    _description = "Shopinvader Product"
    _inherit = ["shopinvader.binding", "abstract.url", "seo.title.mixin"]
    _inherits = {"product.template": "record_id"}

    record_id = fields.Many2one(
        "product.template", required=True, ondelete="cascade", index=True
    )
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    short_description = fields.Html()
    description = fields.Html()
    shopinvader_variant_ids = fields.One2many(
        "shopinvader.variant", "shopinvader_product_id", "Shopinvader Variant"
    )
    active = fields.Boolean(default=True, inverse="_inverse_active")
    url_key = fields.Char(compute_sudo=True)
    use_shopinvader_product_name = fields.Boolean(
        related="backend_id.use_shopinvader_product_name",
        store=True,
        readonly=True,
    )
    shopinvader_name = fields.Char(
        string="Name",
        help="Name for shopinvader, if not set the product name will be used.",
    )
    shopinvader_display_name = fields.Char(
        compute="_compute_name", readonly=True
    )
    shopinvader_categ_ids = fields.Many2many(
        comodel_name="shopinvader.category",
        compute="_compute_shopinvader_category",
        string="Shopinvader Categories",
    )

    _sql_constraints = [
        (
            "record_uniq",
            "unique(backend_id, record_id, lang_id)",
            "A product can only have one binding by backend and lang.",
        )
    ]

    @api.depends("use_shopinvader_product_name", "shopinvader_name")
    def _compute_name(self):
        for record in self:
            if record.use_shopinvader_product_name and record.shopinvader_name:
                record.shopinvader_display_name = record.shopinvader_name
            else:
                record.shopinvader_display_name = record.name

    @api.multi
    def _build_seo_title(self):
        """
        Build the SEO product name
        :return: str
        """
        self.ensure_one()
        return u"{} | {}".format(
            self.name or u"", self.backend_id.website_public_name or u""
        )

    @api.multi
    def _inverse_active(self):
        self.filtered(lambda p: not p.active).mapped(
            "shopinvader_variant_ids"
        ).write({"active": False})
        self.filtered(lambda p: p.active).mapped(
            "shopinvader_variant_ids"
        ).write({"active": True})

    def _get_categories(self):
        self.ensure_one()
        return self.categ_id

    def _compute_shopinvader_category(self):
        for record in self:
            ids = []
            categs = record._get_categories()
            for categ in categs:
                parents = self.env["shopinvader.category"].search(
                    [
                        ("record_id", "parent_of", categ.id),
                        ("backend_id", "=", record.backend_id.id),
                        ("lang_id", "=", record.lang_id.id),
                    ]
                )
                ids += parents.ids
            record.shopinvader_categ_ids = ids

    def _prepare_shopinvader_variant(self, variant):
        values = {"record_id": variant.id, "shopinvader_product_id": self.id}
        # If the variant is not active, we have to force active = False
        if not variant.active:
            values.update({"active": variant.active})
        return values

    def _get_variants(self):
        return self.product_variant_ids

    def _create_shopinvader_variant(self):
        """
        Create missing shopinvader.variant and return new just created
        :return: shopinvader.variant recordset
        """
        self.ensure_one()
        self_ctx = self.with_context(active_test=False)
        shopinv_variant_obj = self_ctx.env["shopinvader.variant"]
        shopinv_variants = shopinv_variant_obj.browse()
        for variant in self_ctx._get_variants():
            if not shopinv_variant_obj.search_count(
                [
                    ("record_id", "=", variant.id),
                    ("shopinvader_product_id", "=", self.id),
                ]
            ):
                vals = self_ctx._prepare_shopinvader_variant(variant)
                shopinv_variants |= shopinv_variant_obj.create(vals)
        return shopinv_variants

    @api.model
    def create(self, vals):
        binding = super(ShopinvaderProduct, self).create(vals)
        if self.env.context.get("map_children"):
            binding._create_shopinvader_variant()
        return binding

    def _get_url_keywords(self):
        self.ensure_one()
        keywords = super(ShopinvaderProduct, self)._get_url_keywords()
        if self.default_code:
            keywords.append(self.default_code)
        return keywords

    @api.multi
    @api.depends("lang_id", "record_id.name")
    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderProduct, self).default_get(fields_list)
        if "backend_id" in fields_list:
            backend = self.env["shopinvader.backend"].search([], limit=1)
            res["backend_id"] = backend.id
        return res

    @api.multi
    def toggle_published(self):
        """
        Toggle the active field
        :return: dict
        """
        actual_active = self.filtered(lambda s: s.active).with_prefetch(
            self._prefetch
        )
        actual_inactive = self - actual_active
        actual_inactive = actual_inactive.with_prefetch(self._prefetch)
        if actual_inactive:
            actual_inactive.write({"active": True})
        if actual_active:
            actual_active.write({"active": False})
        return {}

    def _redirect_existing_url(self):
        """
        During unbind, we have to redirect existing urls to the (first) related
        shopinvader category.
        :return: bool
        """
        for record in self.filtered(lambda p: p.url_url_ids):
            # Active category without children
            categs = record.shopinvader_categ_ids.filtered(
                lambda c: c.active and not c.shopinvader_child_ids
            )
            if categs:
                categ = fields.first(categs)
                record.url_url_ids.write(
                    {
                        "redirect": True,
                        "model_id": "{},{}".format(categ._name, categ.id),
                    }
                )
        return True

    def unlink(self):
        # Call unlink manually to be sure to trigger
        # shopinvader variant unlink constraint
        self.mapped("shopinvader_variant_ids").unlink()
        return super(ShopinvaderProduct, self).unlink()
