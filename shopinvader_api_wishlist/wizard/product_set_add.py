# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductSetAdd(models.TransientModel):
    _inherit = "product.set.add"

    def prepare_sale_order_line_data(self, set_line, max_sequence=0):
        # check if user is in the group of shopinvader_wishlist_user_group
        # if true run super in sudo mode
        self_super = self
        if self.env.user.has_group(
            "shopinvader_api_wishlist.shopinvader_wishlist_user_group"
        ):
            self_super = self.sudo()
        return super(ProductSetAdd, self_super).prepare_sale_order_line_data(
            set_line, max_sequence
        )
