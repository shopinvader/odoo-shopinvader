# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    hierarchical_categories = fields.Serialized(
        compute="_compute_shopinvader_category",
        string="Hierarchical Categories",
    )

    def _category_to_elastic_index_data(self, shopinvader_category):
        categ = shopinvader_category
        parent_names = []
        parent_id = categ.parent_id
        while parent_id:
            parent_names.append(parent_id.name)
            parent_id = parent_id.parent_id
        return {
            "level": categ.level + 1,
            "value": categ.name,
            "ancestors": parent_names,
            "order": categ.sequence,
        }

    def _compute_shopinvader_category(self):
        super(ShopinvaderProduct, self)._compute_shopinvader_category()
        for record in self:
            values = []
            for categ in record.shopinvader_categ_ids:
                values.append(self._category_to_elastic_index_data(categ))
            record.hierarchical_categories = values
