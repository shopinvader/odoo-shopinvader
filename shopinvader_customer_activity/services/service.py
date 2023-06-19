# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def dispatch(self, method_name, *args, params=None):
        res = super().dispatch(method_name, *args, params=params)
        if self.invader_partner_user:
            self.invader_partner_user._log_active_date()
        return res
