# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _handle_utm(self, record):
        if "utm.mixin" in record._inherit_module and hasattr(self.work, "utm"):
            record.shopinvader_add_utm(self.work.utm)

    def dispatch(self, method_name, *args, params=None):
        res = super().dispatch(method_name, *args, params=params)
        if self._expose_model and res.get("data", {}).get("id"):
            record = self.env[self._expose_model].browse(res["data"]["id"])
            self._handle_utm(record)
        return res
