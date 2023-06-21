# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.exceptions import AccessError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    @restapi.method(
        routes=[(["/impersonate"], "GET")],
        input_param=restapi.CerberusValidator("_validator_impersonate"),
    )
    def impersonate(self, email=None, token=None):
        shop_partner = self.env["shopinvader.partner"]._get_from_token(email, token)
        if shop_partner:
            _logger.info("Shopinvader customer impersonate: %s", email)
            customer = self._to_customer_info(shop_partner.record_id)
            return {
                "store_cache": {"customer": customer},
                "force_authenticate_customer": shop_partner.email,
                "redirect_to": shop_partner.backend_id.location,
            }
        else:
            raise AccessError(_("Invalid impersonate token"))

    def _validator_impersonate(self):
        return {
            "token": {"type": "string", "required": True},
            "email": {"type": "string", "required": True},
        }
