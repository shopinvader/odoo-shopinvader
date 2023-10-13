# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shopinvader_categ_ids = fields.Many2many(
        comodel_name="product.category",
        compute="_compute_shopinvader_category",
        string="Shopinvader Categories",
    )

    def _get_categories(self):
        self.ensure_one()
        return self.categ_id

    @api.model
    def _get_parent_categories(self, categ_ids):
        return self.env["product.category"].search(
            [("id", "parent_of", set(categ_ids))]
        )

    @api.depends("categ_id", "categ_id.parent_id")
    def _compute_shopinvader_category(self):
        prod_by_categ = {}
        for record in self:
            categs = tuple(sorted(record._get_categories().ids))
            prod_by_categ.setdefault(categs, []).append(record.id)
            # prod1.categories = catA, catB, catC
            # prod2.categories = catA
            # prod3.categories = catA, catB, catC
            # {
            #   (catA.id): [prod2.id],
            #   (catA.id,catB.id,catC.id): [prod1.id, prod3.id]
            # }

        for categ_ids, prod_ids in prod_by_categ.items():
            categories = self._get_parent_categories(categ_ids)
            self.browse(prod_ids).update({"shopinvader_categ_ids": categories.ids})
