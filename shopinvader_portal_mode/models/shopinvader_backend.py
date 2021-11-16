# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    sale_order_portal_mode = fields.Boolean(
        default=False,
        string="Display all orders",
        help="Display all orders for the customer, not just the ones from the shop",
        sparse="sale_settings",
    )
