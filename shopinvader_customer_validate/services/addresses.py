# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _prepare_params(self, params, mode="create"):
        params = super()._prepare_params(params, mode=mode)
        if mode == "create":
            params["is_shopinvader_active"] = self.partner_validator.enabled_by_params(
                params, "address"
            )
        return params
