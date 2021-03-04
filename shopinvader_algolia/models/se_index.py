# Copyright 2019 Akretion (http://www.akretion.com).
# @author Florian da Costa <florian?dacosta@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.connector_algolia.utils import data_merge


class SeIndex(models.Model):
    _inherit = "se.index"

    def _get_settings(self):
        settings = super(SeIndex, self)._get_settings()
        model = self.model_id.model
        # TODO check backend se type and call specific algolia method?
        facetting_values = {}
        if hasattr(self.env[model], "_get_facetting_values"):
            facetting_values = self.env[model]._get_facetting_values(
                self.backend_id, self.lang_id
            )
        if facetting_values:
            data_merge(settings, {"attributesForFaceting": facetting_values})
        return settings
