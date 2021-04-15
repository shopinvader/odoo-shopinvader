# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    featured = fields.Boolean(help="Add featured flag on product variant")
