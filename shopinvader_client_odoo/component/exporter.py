# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class ClientSiteExporter(Component):
    _inherit = "shopinvader.site.exporter"

    def _get_external_id(self):
        # we don't actually care about the ext ID for the website
        # because we use api key to auto retrieve the record on the client.
        return self.backend_record.client_api_key