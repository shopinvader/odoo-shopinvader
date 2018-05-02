# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.fields import first


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    price = fields.Serialized(
        'Shopinvader Price',
        compute='_compute_price',
    )

    def _compute_price(self):
        """
        Compute the Serialized price field with prices for each sale profile
        of related backend
        :return:
        """
        for record in self:
            prices = {}
            for sale_profile in record.backend_id.sale_profile_ids:
                fposition = first(sale_profile.fiscal_position_ids)
                price = record._get_price(
                    sale_profile.pricelist_id, fposition,
                    record.backend_id.company_id)
                prices.update({
                    sale_profile.code: price,
                })
            record.price = prices
