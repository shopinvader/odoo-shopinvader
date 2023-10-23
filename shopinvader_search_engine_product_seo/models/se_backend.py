# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackend(models.Model):
    _inherit = "se.backend"

    seo_title_suffix = fields.Char(
        translate=True,
        help="Used for products name referencing (e.g. public name of your website)",
    )
