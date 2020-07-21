# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopinvaderSiteExportMapper(Component):
    _inherit = ["shopinvader.site.export.mapper"]

    # matching $searchengine_name + '_config'
    def _algolia_config(self, se_backend, config):
        if (
            self.options["force"]
            or not config.get("application_id")
            or not config.get("api_key")
        ):
            spec_backend = se_backend.specific_backend
            config.update(
                {
                    "application_id": spec_backend.algolia_app_id,
                    "api_key": spec_backend.algolia_api_key_public,
                }
            )
        return config
