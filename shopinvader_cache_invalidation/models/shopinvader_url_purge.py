# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderUrlPurge(models.Model):
    _name = "shopinvader.url.purge"
    _description = "List of url to purge from cache"

    url = fields.Char(required=True)
    purge_type_id = fields.Many2one(
        "shopinvader.url.purge.type", string="Purge Type", required=True
    )
    backend_id = fields.Many2one("shopinvader.backend", string="Backend", required=True)
    date_last_purge = fields.Datetime("Last Purge Date", readonly=True)
    manual = fields.Boolean(default=True, readonly=True, required=True)
    state = fields.Selection(
        [
            ("to_purge", "To purge"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        readonly=True,
    )
    error = fields.Char(readonly=True)

    def _request_purge(self, url_key, model_name, model_description, backend_id):
        record = self.search(
            [
                ("url", "=", url_key),
                ("backend_id", "=", backend_id),
            ]
        )
        if record:
            record.state = "to_purge"
        else:
            purge_type = self.env["shopinvader.url.purge.type"].get_or_create(
                model_name, model_description
            )
            record = self.create(
                {
                    "url": url_key,
                    "state": "to_purge",
                    "purge_type_id": purge_type.id,
                    "backend_id": backend_id,
                    "manual": False,
                }
            )

    # use by cron
    def purge_url(self):
        for backend in self.backend_id:
            s = requests.Session()
            s.headers.update(
                {"X-force-cache-refresh": self.backend_id.cache_refresh_secret}
            )
            for record in self:
                if record.backend_id == backend:
                    url = f"{record.backend_id.location}/{record.url}"
                    try:
                        response = s.get(url)
                        if response.status_code != 200:
                            raise Exception(
                                "Response Error code %s %s",
                                response.status_code,
                                response.text,
                            )
                        self.write(
                            {
                                "date_last_purge": fields.Datetime.now(),
                                "state": "done",
                                "error": None,
                            }
                        )
                    except Exception as e:
                        _logger.error("Fail to purge %s", e)
                        self.error = str(e)
                        self.state = "failed"
                        continue


class ShopinvaderUrlPurgeType(models.Model):
    _name = "shopinvader.url.purge.type"

    code = fields.Char(readonly=True)
    name = fields.Char(required=True)

    def get_or_create(self, model_name, model_description):
        res = self.search([("code", "=", model_name)])
        if not res:
            res = self.create({"code": model_name, "name": model_description})
        return res
