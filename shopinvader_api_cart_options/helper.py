# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import namedtuple

from odoo import models

from odoo.addons.shopinvader_api_cart.schemas import CartTransaction

from .schemas import SaleLineOptions


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    def _get_transaction_key(self, transaction: CartTransaction):
        """
        Override the method to add the options defined in the SaleLineOptions
        """
        key = super()._get_transaction_key(transaction)
        options = tuple(SaleLineOptions._get_assembled_cls().model_fields.keys())
        return namedtuple(key.__class__.__name__, key._fields + options)(
            *key,
            *tuple(
                getattr(transaction.options, key) if transaction.options else None
                for key in options
            ),
        )
