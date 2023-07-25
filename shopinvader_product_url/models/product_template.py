# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "abstract.url"]
    _name = "product.template"

    def _get_keyword_fields(self):
        return super()._get_keyword_fields() + ["default_code"]
