# Copyright 2024 ACSONE SA (https://acsone.eu).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from typing import Annotated, Any
from urllib.parse import urljoin

from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse

from odoo import api, models

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment.models.payment_transaction import PaymentTransaction
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import (
    Payable,
    add_query_params_in_url,
    tx_state_to_redirect_status,
)
from odoo.addons.shopinvader_api_payment.schemas import TransactionProcessingValues

_logger = logging.getLogger(__name__)


@payment_router.post("/payment/providers/custom/pending")
def custom_payment_pending_msg(
    payable: str,
    frontend_redirect_url: str,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    try:
        payable_obj = Payable.decode(odoo_env, payable)
    except Exception as e:
        _logger.info("Could not decode payable")
        raise HTTPException(403) from e
    tx_sudo = odoo_env["payment.transaction"].sudo().browse(payable_obj.transaction_id)
    tx_sudo._set_pending()
    tx_sudo._execute_callback()
    return RedirectResponse(
        url=add_query_params_in_url(
            frontend_redirect_url,
            {
                "status": tx_state_to_redirect_status(tx_sudo.state),
                "pending_message": tx_sudo.provider_id.pending_msg,
            },
        ),
        status_code=303,
    )


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_payment.payment_router.helper"

    def _update_payable_with_transaction(
        self,
        payable: str,
        tx_sudo: PaymentTransaction,
    ) -> str:
        try:
            payable_obj = Payable.decode(self.env, payable)
        except Exception as e:
            _logger.info("Could not decode payable")
            raise HTTPException(403) from e
        payable_obj.transaction_id = tx_sudo.id
        return payable_obj.encode(self.env)

    def _get_custom_redirect_form_html(
        self, tx_sudo: PaymentTransaction, payable: str, frontend_redirect_url: str
    ) -> str:
        shopinvader_api_payment_base_url = tx_sudo.env.context.get(
            "shopinvader_api_payment_base_url", ""
        )
        payable_with_transaction = self._update_payable_with_transaction(
            payable, tx_sudo
        )
        redirect_url = urljoin(shopinvader_api_payment_base_url, "custom/pending")
        return f"""\n
        <form method=\"post\"
        action=\"{redirect_url}\">\n
                    <input type=\"hidden\" name=\"Data\"
                    value=\"payable={payable_with_transaction}|
                    frontend_redirect_url={frontend_redirect_url}
                    \"/>\n
                          </form>"""

    def _get_tx_processing_values(
        self, tx_sudo: PaymentTransaction, **kwargs: Any
    ) -> TransactionProcessingValues:
        tx_processing_values = super()._get_tx_processing_values(tx_sudo, **kwargs)
        if tx_sudo.provider_id.code == "custom":
            tx_processing_values.redirect_form_html = (
                self._get_custom_redirect_form_html(
                    tx_sudo,
                    kwargs.get("payable", ""),
                    kwargs.get("frontend_redirect_url", ""),
                )
            )
        return tx_processing_values
