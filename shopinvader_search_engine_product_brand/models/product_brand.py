# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = ["product.brand", "se.indexable.record"]
