# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).


import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SeBinding(models.AbstractModel):
    _inherit = "se.binding"

    def synchronize(self):
        res = super().synchronize()
        # some fields "url_key" are missing in self.data
        url_keys = {binding.data.get("url_key") for binding in self}

        for url_key in url_keys:
            if url_key:
                self.env["shopinvader.url.purge"]._request_purge(
                    url_key, self._name, self._description, self.se_backend_id
                )
        return res
