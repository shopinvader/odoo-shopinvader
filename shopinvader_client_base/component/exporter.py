# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class ClientExporter(Component):
    _name = "shopinvader.client.exporter"
    _inherit = ["generic.exporter", "shopinvader.client.connector"]
    _usage = "record.exporter"

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)

    def _create(self, record):
        result = super()._create(record)
        return result["_id"]


class ClientSiteExporter(Component):
    _name = "shopinvader.site.exporter"
    _inherit = ["generic.exporter", "shopinvader.client.connector"]
    _usage = "record.exporter"
    _apply_on = "shopinvader.backend"

    def _get_external_id(self):
        return self.backend_record.handle

    def run(self, fields=None):
        self.binding = self.backend_record
        self.external_id = self._get_external_id()
        map_record = self._map_data()
        data = self._update_data(map_record, fields=fields)
        self._update(data)
