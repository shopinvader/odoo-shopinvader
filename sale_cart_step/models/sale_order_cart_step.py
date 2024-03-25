# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderCartStep(models.Model):
    _name = "sale.order.cart.step"
    _description = "Cart Step"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True, copy=False)

    _sql_constraints = [
        ("code_uniq", "unique (code, active)", "Active step code must be unique!")
    ]
