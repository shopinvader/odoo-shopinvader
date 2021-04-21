# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Product(models.Model):
    _inherit = ["product.product", "rating.mixin"]
    _name = "product.product"
