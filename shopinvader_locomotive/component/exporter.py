# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.addons.component.core import Component


class LocomotiveExporter(Component):
    _name = "locomotive.exporter"
    _inherit = ["generic.exporter", "base.locomotive.connector"]
    _usage = "record.exporter"

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        # As we push a json we always need to push all info
        return self._create_data(map_record, fields=None, **kwargs)

    def _create(self, record):
        result = super()._create(record)
        return result["_id"]


class LocomotiveSiteExporter(Component):
    _inherit = ["generic.exporter", "base.locomotive.connector"]
    _name = "locomotive.site.exporter"
    _usage = "record.exporter"
    _apply_on = "shopinvader.backend"

    def _get_exising_metafields(self):
        site_infos = self.backend_adapter._get_site(self.backend_record.handle)
        return json.loads(site_infos["metafields"])

    def run(self, fields=None, force=False):
        self.binding = self.backend_record
        self.external_id = self.backend_record.handle
        map_record = self._map_data()
        data = self._update_data(
            map_record,
            fields=fields,
            current_values=self._get_exising_metafields(),
            force=force,
        )
        self._update(data)
