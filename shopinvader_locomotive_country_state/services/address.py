# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _prepare_params(self, params, mode="create"):
        # TODO: Fix on shopinvader main module
        if "state" in params:
            state = params.get("state")
            if not state.get("id"):
                params["state_id"] = False
        return super()._prepare_params(params, mode=mode)
