# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductFilter(models.Model):
    _inherit = "product.filter"

    visible = fields.Boolean(
        default=True,
        help="* ON: the filter will be pushed to site settings, "
        "therefore it is going to be visible in frontend faceted search;\n"
        "* OFF: the filter will be usable for searching but invisible as filter.",
    )
