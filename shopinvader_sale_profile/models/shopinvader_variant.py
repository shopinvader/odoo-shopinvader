# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.fields import first


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_all_price(self):
        # Override. Update prices with each sale profile of related backend
        res = super()._get_all_price()
        for sale_profile in self.backend_id.sale_profile_ids:
            fposition = first(sale_profile.fiscal_position_ids)
            price = self._get_price(
                pricelist=sale_profile.pricelist_id,
                fposition=fposition,
                company=self.backend_id.company_id,
            )
            res.update({sale_profile.code: price})
        return res
