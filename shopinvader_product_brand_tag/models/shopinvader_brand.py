# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderBrand(models.Model):
    _inherit = "shopinvader.brand"

    serialized_tag_ids = Serialized(compute="_compute_serialized_tag_ids")

    @api.depends("tag_ids")
    def _compute_serialized_tag_ids(self):
        for rec in self:
            rec.serialized_tag_ids = rec.tag_ids.ids
