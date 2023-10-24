# Copyright 2018 ACSONE SA/NV
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    def force_recompute_all_binding_index(self):
        records = self.filtered(
            lambda r: not r.product_manual_binding and r.product_assortment_id
        )
        for record in records:
            record._autobind_product_from_assortment()
        return super().force_recompute_all_binding_index()
