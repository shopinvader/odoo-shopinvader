# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    partner_pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Partner Pricelist",
        help="Pricelist to apply on every partner created from this channel",
    )
