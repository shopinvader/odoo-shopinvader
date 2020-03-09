# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SalePromotionRule(models.Model):
    _inherit = "sale.promotion.rule"

    @api.model
    def compute_promotions(self, orders):
        """
        Inherit to add specific context to bypass shopinvader_write_date
        """
        self_ctx = self.with_context(skip_shopinvader_write_date=True)
        orders = orders.with_context(skip_shopinvader_write_date=True)
        return super(SalePromotionRule, self_ctx).compute_promotions(orders)
