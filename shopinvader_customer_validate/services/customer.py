# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component

from ..models.shopinvader_partner import STATE_ACTIVE, STATE_PENDING


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _prepare_params(self, params, mode="create"):
        params = super()._prepare_params(params, mode=mode)
        if mode == "create":
            enabled = self.partner_validator.enabled_by_params(params, "profile")
            params["state"] = STATE_ACTIVE if enabled else STATE_PENDING
        return params
