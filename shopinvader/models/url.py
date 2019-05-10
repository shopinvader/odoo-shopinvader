# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UrlUrl(models.Model):
    _inherit = "url.url"

    model_id = fields.Reference(
        selection_add=[
            ("shopinvader.product", "ShopInvader Product"),
            ("shopinvader.category", "ShopInvader Category"),
        ]
    )
