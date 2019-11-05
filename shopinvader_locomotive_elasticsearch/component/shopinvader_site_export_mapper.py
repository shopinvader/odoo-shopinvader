# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class ShopinvaderSiteExportMapper(Component):
    _inherit = ["shopinvader.site.export.mapper"]

    # matching $searchengine_name + '_config'
    def _elasticsearch_config(self, se_backend, config):
        if self.options["force"] or not config.get("url"):
            config["url"] = se_backend.specific_backend.es_server_host
        return config
