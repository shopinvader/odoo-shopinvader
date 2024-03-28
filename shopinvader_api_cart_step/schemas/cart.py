# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_cart.schemas import (
    CartUpdateInput as BaseCartUpdateInput,
)


class CartUpdateInput(BaseCartUpdateInput, extends=True):

    current_step: str | None = None
    next_step: str | None = None

    def convert_to_sale_write(self):
        vals = super().convert_to_sale_write()
        # NOTE: is not possible to use `env` to retrive data here
        return vals
