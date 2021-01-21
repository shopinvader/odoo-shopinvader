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
    lang_ids = fields.Many2many(
        string="Langs",
        comodel_name="res.lang",
        ondelete="cascade",
        help="List of langs for which a binding must exists. If not "
        "specified, the list of langs defined on the backend is used.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderVariantBindingWizard, self).default_get(fields_list)
        backend_id = self.env.context.get("active_id", False)
        if backend_id:
            backend = self.env["shopinvader.backend"].browse(backend_id)
            res["backend_id"] = backend_id
            res["lang_ids"] = [(6, None, backend.lang_ids.ids)]
        return res

    def _get_langs_to_bind(self):
        self.ensure_one()
        return self.lang_ids or self.backend_id.lang_ids

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
                ("lang_id", "in", self._get_langs_to_bind().ids),
            ]
        )
        ret = defaultdict(dict)
        for bt in binded_templates:
            ret[bt.record_id][bt.lang_id] = bt
        for product in self.mapped("product_ids.product_tmpl_id"):
            product_tmpl_id = product
            bind_records = ret.get(product_tmpl_id)
            for lang_id in self._get_langs_to_bind():
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

    def bind_products(self):
        for wizard in self:
            binded_templates = wizard._get_binded_templates()
            binding = self.env["shopinvader.variant"]
            for product in wizard.product_ids:
                binded_products = binded_templates[product.product_tmpl_id]
                for lang_id in wizard._get_langs_to_bind():
                    for shopinvader_product in binded_products[lang_id]:
                        binded_variants = shopinvader_product.shopinvader_variant_ids
                        bind_record = binded_variants.filtered(
                            lambda p: p.record_id == product
                        )
                        if not bind_record:
                            # fmt: off
                            data = {
                                "record_id": product.id,
                                "backend_id": wizard.backend_id.id,
                                "shopinvader_product_id":
                                    shopinvader_product.id,
                            }
                            # fmt: on
                            binding.create(data)
                        elif not bind_record.active:
                            bind_record.write({"active": True})
            wizard.backend_id.auto_bind_categories()

    @api.model
    def bind_langs(self, backend, lang_ids):
        """
        Ensure that a shopinvader.variant exists for each lang_id. If not,
        create a new binding for the missing lang. This method is usefull
        to ensure that when a lang is added to a backend, all the binding
        for this lang are created for the existing binded products
        :param backend: backend record
        :param lang_ids: list of lang ids we must ensure that a binding exists
        :return:
        """
        binded_products = self.env["product.product"].search(
            [("shopinvader_bind_ids.backend_id", "=", backend.id)]
        )
        # use in memory record to avoid the creation of useless records into
        # the database
        # by default the wizard check if a product is already binded so we
        # can use it by giving the list of product already binded in one of
        # the specified lang and the process will create the missing one.

        # TODO 'new({})' doesn't work into V13 -> should use model lassmethod
        wiz = self.create(
            {
                "lang_ids": self.env["res.lang"].browse(lang_ids),
                "backend_id": backend.id,
                "product_ids": binded_products,
            }
        )
        wiz.bind_products()
