# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AbstractUrl(models.AbstractModel):
    _inherit = "abstract.url"

    url_key = fields.Char(compute="_compute_url_key")
    redirect_url_key = fields.Serialized(
        compute="_compute_url_key", string="Redirect Url Keys"
    )

    @api.depends("url_ids")
    @api.depends_context("lang", "referential")
    def _compute_url_key(self):
        referential = self._context.get("referential", "global")
        lang = self._context.get("lang", "en_US")
        for record in self:
            record.url_key = record._get_main_url(referential, lang).key
            record.redirect_url_key = record._get_redirect_urls(
                referential, lang
            ).mapped("key")
