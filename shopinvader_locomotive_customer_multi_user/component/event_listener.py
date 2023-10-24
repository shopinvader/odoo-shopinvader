# Copyright 2021 ForgeFlow S.A. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class ShopinvaderBindingListener(Component):
    _name = "shopinvader.binding.event.listener"
    _inherit = "base.connector.listener"

    _apply_on = ["shopinvader.partner"]

    def _get_fields_to_export(self):
        res = super()._get_fields_to_export()
        return res + ["can_manage_users"]
