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
    lang_ids = fields.Many2many(
        string="Langs",
        comodel_name="res.lang",
        ondelete="cascade",
        help="List of langs for which a binding must exists. If not "
        "specified, the list of langs defined on the backend is used.",
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ShopinvaderCategoryBindingWizard, self).default_get(fields_list)
        backend_id = self.env.context.get("active_id")
        if backend_id:
            backend = self.env["shopinvader.backend"].browse(backend_id)
            result.update(
                {
                    "backend_id": backend_id,
                    "lang_ids": [(6, None, backend.lang_ids.ids)],
                }
            )
        return result

    def _get_langs_to_bind(self):
        self.ensure_one()
        return self.lang_ids or self.backend_id.lang_ids

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
            cat_to_bind = categories.filtered(lambda x: x.parent_id.id in parent_ids)
        cat_to_bind = cat_to_bind.with_context(active_test=False)
        if cat_to_bind:
            for category in cat_to_bind:
                binded_categories = category.shopinvader_bind_ids
                bind_record = binded_categories.filtered(
                    lambda p: p.backend_id.id == backend.id and p.lang_id.id == lang.id
                )
                bind_record = bind_record.with_prefetch(binded_categories._prefetch_ids)
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

    def action_bind_categories(self):
        for wizard in self:
            if wizard.child_autobinding:
                categ_ids = wizard.with_context(active_test=False).product_category_ids
                for categ_id in categ_ids:
                    childs_cat = self.env["product.category"].search(
                        [("id", "child_of", categ_id.id)]
                    )
                    if childs_cat:
                        wizard.product_category_ids += childs_cat
            backend = wizard.backend_id
            for lang in wizard._get_langs_to_bind():
                self._bind_categories(backend, lang, wizard.product_category_ids)

    @api.model
    def bind_langs(self, backend, lang_ids):
        """
        Ensure that a shopinvader.CATEGORY exists for each lang_id. If not,
        create a new binding for the missing lang. This method is usefull
        to ensure that when a lang is added to a backend, all the binding
        for this lang are created for the existing binded categories
        :param backend: backend record
        :param lang_ids: list of lang ids we must ensure that a binding exists
        :return:
        """
        binded_categories = self.env["product.category"].search(
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
                "product_category_ids": binded_categories,
            }
        )
        wiz.action_bind_categories()
