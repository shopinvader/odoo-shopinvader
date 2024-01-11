# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import models
from odoo.fields import Command

from odoo.addons.shopinvader_api_payment.routers.utils import Payable
from odoo.addons.shopinvader_api_payment.schemas import TransactionCreate


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_payment.payment_router.helper"

    def _get_additional_transaction_create_values(
        self, data: TransactionCreate
    ) -> dict:
        # Intended to be extended for invoices, carts...
        additional_transaction_create_values = (
            super()._get_additional_transaction_create_values(data)
        )
        payable_obj = Payable.model_validate(json.loads(data.payable))
        if payable_obj.payable_model == "sale.order":
            additional_transaction_create_values["sale_order_ids"] = [
                Command.set([payable_obj.payable_id])
            ]
        return additional_transaction_create_values
