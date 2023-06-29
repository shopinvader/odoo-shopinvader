# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FakeProduct(models.Model):
    _inherit = ["abstract.url"]
    _name = "fake.product"

    code = fields.Char()
    name = fields.Char(translate=True)
    active = fields.Boolean(default=True)

    @api.depends("name")
    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()

    def _get_url_keywords(self):
        return super()._get_url_keywords() + [self.code or ""]
