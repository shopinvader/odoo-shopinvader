# -*- coding: utf-8 -*-
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
        warehouse_ids = warehouse_keys.get("global")
        if warehouse_ids:
            self_ctx = self.with_context(warehouse=warehouse_ids)
        return super(
            ShopinvaderBackend, self_ctx
        )._autobind_product_from_assortment()
