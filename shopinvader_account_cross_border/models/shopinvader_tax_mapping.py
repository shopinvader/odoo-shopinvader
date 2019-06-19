# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderTaxMapping(models.Model):

    _name = "shopinvader.tax.mapping"
    _rec_name = "country_id"
    _description = "Shopinvader Tax Mapping"

    backend_id = fields.Many2one(
        string="Shopinvader Backend",
        comodel_name="shopinvader.backend",
        required=True,
        index=True,
        ondelete="cascade",
    )
    country_id = fields.Many2one(
        string="Country", comodel_name="res.country", required=True, index=True
    )

    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position", string="Fiscal position"
    )

    _sql_constraints = [
        (
            "country_map_uniq",
            "unique(backend_id, country_id)",
            "A mapping already exists for this country.",
        )
    ]
