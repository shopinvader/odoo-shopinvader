# -*- coding: utf-8 -*-
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
        shopinvader_variant_ids = self.env.context.get("active_ids")
        if shopinvader_variant_ids:
            result.update(
                {"shopinvader_category_ids": shopinvader_variant_ids}
            )
        return result

    @api.multi
    def action_unbind_categories(self):
        self.mapped("shopinvader_category_ids")._unbind()
