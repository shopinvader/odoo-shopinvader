# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderCategoryUnbindingWizard(models.TransientModel):
    """
    Wizard used to unbind a shopinvader.category (a product.category on a
    specific backend)
    """

    _name = "shopinvader.category.unbinding.wizard"
    _description = "Wizard to unbind categories from a shopinvader backend"

    shopinvader_category_ids = fields.Many2many(
        "shopinvader.category", string="Categories", ondelete="cascade"
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ShopinvaderCategoryUnbindingWizard, self).default_get(
            fields_list
        )
        shopinvader_category_ids = self.env.context.get("active_ids")
        if shopinvader_category_ids:
            result.update(
                {"shopinvader_category_ids": shopinvader_category_ids}
            )
        return result

    def action_unbind_categories(self):
        self.mapped("shopinvader_category_ids")._unbind()

    @api.model
    def unbind_langs(self, backend, lang_ids):
        """
        Unbind the binded shopinvader.category for the given lang
        :param backend: backend record
        :param lang_ids: list of lang ids we must ensure that no more binding
                          exists
        :return:
        """
        shopinvader_category_ids = self.env["shopinvader.category"].search(
            [("lang_id", "in", lang_ids), ("backend_id", "=", backend.id)]
        )
        shopinvader_category_ids._unbind()
