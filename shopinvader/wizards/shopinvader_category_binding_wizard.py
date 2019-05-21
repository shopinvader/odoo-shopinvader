# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderCategoryBindingWizard(models.TransientModel):
    """
    Wizard used to bind product.category to shopinvader.category
    """

    _name = "shopinvader.category.binding.wizard"
    _description = "Wizard to bind categories to a shopinvader categories"

    backend_id = fields.Many2one(
        "shopinvader.backend",
        "ShopInvader Backend",
        required=True,
        ondelete="cascade",
    )
    product_category_ids = fields.Many2many(
        "product.category", string="Categories", ondelete="cascade"
    )
    child_autobinding = fields.Boolean(
        help="If this option is check, the childs of selected categories"
        " will be automatically binded"
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ShopinvaderCategoryBindingWizard, self).default_get(
            fields_list
        )
        backend_id = self.env.context.get("active_id")
        if backend_id:
            result.update({"backend_id": backend_id})
        return result

    def _bind_categories(self, backend, lang, categories, parent_ids=None):
        """
        This method is used to bind all categories recursively starting
        from the higher level to the lower one
        :param backend: backend on which we need to bind categories
        :param lang: binding language
        :param categories: list of categories selected by user
        :param parent_ids: parent category ids used to filter categories subset
        :return:
        """
        if not parent_ids:
            cat_to_bind = categories.filtered(
                lambda x: x.parent_id.id not in categories.ids
            )
        else:
            cat_to_bind = categories.filtered(
                lambda x: x.parent_id.id in parent_ids
            )
        if cat_to_bind:
            for category in cat_to_bind:
                binded_categories = category.shopinvader_bind_ids
                bind_record = binded_categories.filtered(
                    lambda p: p.backend_id.id == backend.id
                    and p.lang_id.id == lang.id
                )
                bind_record = bind_record.with_prefetch(self._prefetch)
                if not bind_record:
                    data = {
                        "record_id": category.id,
                        "backend_id": backend.id,
                        "lang_id": lang.id,
                    }
                    self.env["shopinvader.category"].create(data)
                elif not bind_record.active:
                    bind_record.write({"active": True})
            self._bind_categories(backend, lang, categories, cat_to_bind.ids)

    @api.multi
    def action_bind_categories(self):
        for wizard in self.with_context(active_test=False):
            if wizard.child_autobinding:
                for categ_id in wizard.product_category_ids:
                    childs_cat = self.env["product.category"].search(
                        [("id", "child_of", categ_id.id)]
                    )
                    if childs_cat:
                        wizard.product_category_ids += childs_cat
            backend = wizard.backend_id
            for lang in wizard.backend_id.lang_ids:
                self._bind_categories(
                    backend, lang, wizard.product_category_ids
                )
