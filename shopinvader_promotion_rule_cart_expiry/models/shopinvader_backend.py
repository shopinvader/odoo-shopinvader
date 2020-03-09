# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.osv import expression


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    @api.multi
    def _get_expiry_cart_domain(self):
        """
        Inherit to add OR to use the shopinvader_write_date.
        :return: list/domain
        """
        super_domain = expression.normalize_domain(
            super(ShopinvaderBackend, self)._get_expiry_cart_domain()
        )
        expiry_date = self._get_expiry_date()
        new_domain = expression.normalize_domain(
            [
                ("shopinvader_backend_id", "in", self.ids),
                ("typology", "=", "cart"),
                ("shopinvader_write_date", "<=", expiry_date),
            ]
        )
        domain = expression.OR([super_domain, new_domain])
        return domain
