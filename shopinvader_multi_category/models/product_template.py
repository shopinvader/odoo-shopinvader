# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_categories(self):
        return self.categ_ids + super()._get_categories()

    @api.depends("categ_id", "categ_id.parent_id", "categ_ids", "categ_ids.parent_id")
    def _compute_shopinvader_category(self):
        return super()._compute_shopinvader_category()
