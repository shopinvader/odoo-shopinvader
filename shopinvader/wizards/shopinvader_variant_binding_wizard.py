# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class ShopinvaderVariantBindingWizard(models.TransientModel):

    _name = "shopinvader.variant.binding.wizard"
    _description = "Wizard to bind products to a shopinvader catalogue"

    backend_id = fields.Many2one(
        string="ShopInvader Backend",
        comodel_name="shopinvader.backend",
        required=True,
        ondelete="cascade",
    )
    product_ids = fields.Many2many(
        string="Products", comodel_name="product.product", ondelete="cascade"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderVariantBindingWizard, self).default_get(
            fields_list
        )
        backend_id = self.env.context.get("active_id", False)
        if backend_id:
            res["backend_id"] = backend_id
        return res

    @api.multi
    def _get_binded_templates(self):
        """
        return a dict of binded shopinvader.product by product template id
        :return:
        """
        self.ensure_one()
        binding = self.env["shopinvader.product"]
        product_template_ids = self.mapped("product_ids.product_tmpl_id")
        binded_templates = binding.with_context(active_test=False).search(
            [
                ("record_id", "in", product_template_ids.ids),
                ("backend_id", "=", self.backend_id.id),
            ]
        )
        ret = defaultdict(dict)
        for bt in binded_templates:
            ret[bt.record_id][bt.lang_id] = bt
        for product in self.mapped("product_ids.product_tmpl_id"):
            product_tmpl_id = product
            bind_records = ret.get(product_tmpl_id)
            for lang_id in self.backend_id.lang_ids:
                bind_record = bind_records and bind_records.get(lang_id)
                if not bind_record:
                    data = {
                        "record_id": product.id,
                        "backend_id": self.backend_id.id,
                        "lang_id": lang_id.id,
                    }
                    ret[product_tmpl_id][lang_id] = binding.create(data)
                elif not bind_record.active:
                    bind_record.write({"active": True})
        return ret

    @api.multi
    def bind_products(self):
        for wizard in self:
            binded_templates = wizard._get_binded_templates()
            binding = self.env["shopinvader.variant"]
            for product in wizard.product_ids:
                binded_products = binded_templates[product.product_tmpl_id]
                for shopinvader_product in binded_products.values():
                    binded_variants = (
                        shopinvader_product.shopinvader_variant_ids
                    )
                    bind_record = binded_variants.filtered(
                        lambda p: p.record_id == product
                    )
                    if not bind_record:
                        data = {
                            "record_id": product.id,
                            "backend_id": wizard.backend_id.id,
                            "shopinvader_product_id": shopinvader_product.id,
                        }
                        binding.create(data)
                    elif not bind_record.active:
                        bind_record.write({"active": True})
            wizard.backend_id.auto_bind_categories()
