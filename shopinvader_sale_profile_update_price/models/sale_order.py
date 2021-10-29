# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_sale_pricelist(self):
        """
        Inherit to use the pricelist set on the sale profile (if set)
        :return: product.pricelist recordset
        """
        pricelist = super()._get_sale_pricelist()
        if self.shopinvader_backend_id:
            shopinvader_partner = self.partner_id.shopinvader_bind_ids.filtered(
                lambda b: b.backend_id == self.shopinvader_backend_id
                and b.sale_profile_id.pricelist_id
            )
            if shopinvader_partner:
                pricelist = shopinvader_partner.sale_profile_id.pricelist_id
        return pricelist
