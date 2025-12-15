# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_default_warehouse_id = fields.Many2one(
        "stock.warehouse",
        help="Default warehouse used for sales orders created for this "
        "customer in Shopinvader.",
    )
