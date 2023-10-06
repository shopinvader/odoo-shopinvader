# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    @api.multi
    def _autobind_product_from_assortment(self):
        """
        Inherit to use warehouses used to export in json also to bind
        the assortment.
        Useful in case of search on stock quantities.
        :return:
        """
        self.ensure_one()
        self_ctx = self
        warehouse_keys = self._get_warehouse_list_for_export()
        wh_key_tuple = warehouse_keys.get("global")
        if wh_key_tuple:
            warehouse_ids, location_ids = wh_key_tuple
            if location_ids:
                self_ctx = self.with_context(location=location_ids)
            else:
                self_ctx = self.with_context(warehouse=warehouse_ids)
        return super(
            ShopinvaderBackend, self_ctx
        )._autobind_product_from_assortment()
