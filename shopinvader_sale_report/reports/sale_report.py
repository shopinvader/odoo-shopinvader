# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend", string="Shopinvader backend"
    )

    @api.model
    def _select(self):
        select_query = super(SaleReport, self)._select()
        select_backend = "s.shopinvader_backend_id AS shopinvader_backend_id"
        select_query += ", " + select_backend
        return select_query

    @api.model
    def _group_by(self):
        group_by_query = super(SaleReport, self)._group_by()
        group_by_query += ", s.shopinvader_backend_id"
        return group_by_query
