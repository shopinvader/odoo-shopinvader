# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends

from odoo import api, models
from odoo.fields import Command

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.shopinvader_api_payment.routers.utils import Payable
from odoo.addons.shopinvader_api_payment.schemas import TransactionCreate


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_payment.payment_router.helper"

    def _get_additional_transaction_create_values(
        self,
        data: TransactionCreate,
        odoo_env: Annotated[api.Environment, Depends(odoo_env)],
    ) -> dict:
        # Intended to be extended for invoices, carts...
        additional_transaction_create_values = (
            super()._get_additional_transaction_create_values(data, odoo_env)
        )
        payable_obj = Payable.decode(odoo_env, data.payable)
        if payable_obj.payable_model == "sale.order":
            sale_order_model = (
                self.env["ir.model"].sudo().search([("model", "=", "sale.order")])
            )
            additional_transaction_create_values.update(
                {
                    "sale_order_ids": [Command.set([payable_obj.payable_id])],
                    "callback_method": "_action_confirm_cart_from_tx",
                    "callback_model_id": sale_order_model.id,
                    "callback_res_id": payable_obj.payable_id,
                }
            )
        return additional_transaction_create_values
