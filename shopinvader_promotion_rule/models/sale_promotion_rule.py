# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SalePromotionRule(models.Model):
    _inherit = "sale.promotion.rule"

    restriction_shopinvader_backend_ids = fields.Many2many(
        string="Shopinvader backend restriction",
        comodel_name="shopinvader.backend",
        column1="sale_promotion_rule_id",
        column2="backend_id",
        relation="sale_promo_rule_shop_backend",
        help="Determine on which backends this promotion rule could NOT be "
        "applied. If it set, this promo will be applied on all "
        "others backends.\n"
        "Let it empty to disable the restriction.",
    )

    @api.model
    def _get_restrictions(self):
        """
        Inherit add the shopinvader_backend restriction
        :return: list of str
        """
        restrictions = super(SalePromotionRule, self)._get_restrictions()
        restrictions.append("shopinvader_backend")
        return restrictions

    def _check_valid_shopinvader_backend(self, order):
        """
        If the current promotion doesn't have any backend restriction,
        return True.
        If it has restriction, check on which backend the SO is.
        (return also True if the order is not related to a backend).
        If no backend, it should return True.
        :param order: sale.order recordset
        :return: bool
        """
        self.ensure_one()
        if (
            not self.restriction_shopinvader_backend_ids
            or not order.shopinvader_backend_id
        ):
            return True
        return (
            order.shopinvader_backend_id
            not in self.restriction_shopinvader_backend_ids
        )
