# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ShortProductCategory as BaseShortProductCategory,
)


class ShortProductCategory(BaseShortProductCategory, extends=True):
    @classmethod
    def _get_parent(cls, odoo_rec):
        return odoo_rec.shopinvader_parent_id

    @classmethod
    def _get_children(cls, odoo_rec):
        return odoo_rec.shopinvader_child_ids
