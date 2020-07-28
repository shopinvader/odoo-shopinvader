# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufactured_for_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        domain=[("customer_rank", ">", 0)],
        string="Manufactured for",
    )
