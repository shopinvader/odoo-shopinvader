# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    @api.onchange("partner_shipping_id", "partner_id")
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is
        modified.
        """
        if self.shopinvader_backend_id and self.partner_shipping_id:
            country_code = self.partner_shipping_id.country_id.code
            mapping = self.shopinvader_backend_id.tax_mapping_ids.filtered(
                lambda t: t.country_id.code == country_code
            )
            if mapping and mapping.fiscal_position_id:
                self.fiscal_position_id = mapping.fiscal_position_id
                return {}
        return super(SaleOrder, self).onchange_partner_shipping_id()
