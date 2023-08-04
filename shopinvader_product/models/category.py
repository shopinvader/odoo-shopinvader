# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "abstract.url"]
