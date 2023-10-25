# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPackagingLevel(models.Model):
    _inherit = "product.packaging.level"

    shopinvader_display = fields.Boolean(
        help="Include this packaging into Shopinvader product metadata.",
        default=True,
    )
