# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderUrlPurge(models.Model):
    _name = "shopinvader.url.purge"
    _description = "List of url to purge from cache"

    url = fields.Char(required=True)
    to_purge = fields.Boolean(default=True)
    purge_type_id = fields.Many2one("shopinvader.url.purge.type", string="Purge Type")
    backend_id = fields.Many2one("se.backend", string="Backend Search Engine")
    date_last_purge = fields.Datetime("Last Purge Date", readonly=True)
    manual = fields.Boolean(default=True, readonly=True)

    def _request_purge(self, url_key, model_name, model_description, se_backend):
        record = self.search([("url", "=", url_key)])
        if record:
            record.to_purge = True
        else:
            purge_type = self.env["shopinvader.url.purge.type"].get_or_create(
                model_name, model_description
            )

            record = self.create(
                {
                    "url": url_key,
                    "to_purge": True,
                    "purge_type_id": purge_type.id,
                    "backend_id": se_backend.id,
                    "manual": False,
                }
            )


class ShopinvaderUrlPurgeType(models.Model):
    _name = "shopinvader.url.purge.type"

    code = fields.Char()
    name = fields.Char()

    def get_or_create(self, model_name, model_description):
        res = self.search([("code", "=", model_name)])
        if not res:
            res = self.create({"code": model_name, "name": model_description})
        return res
