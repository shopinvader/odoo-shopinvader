# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _name = "shopinvader.backend"
    _inherit = ["shopinvader.backend", "connector.backend"]
    # TODO: is this really used?
    _backend_name = "replace_me_with_your_client_name"

    client_data = fields.Serialized()
    location = fields.Char(required=True, sparse="client_data")
    # TODO: this field probably should stay only in locomotive client
    handle = fields.Char(
        help="Unique key to identify your site "
             "(in case the client supports multiple websites",
        sparse="client_data",
    )
    currency_ids = fields.Many2many(
        comodel_name="res.currency", string="Currency"
    )

    def synchronize_metadata(self):
        return self._export_settings_store()

    @api.model
    def _scheduler_synchronize_currency(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).synchronize_currency()

    def synchronize_currency(self):
        return self._export_metafields_store(fields=["currency_ids"])

    def _export_settings_store(self, fields=None):
        for record in self:
            with record.work_on(record._name) as work:
                exporter = work.component(usage="record.exporter")
                exporter.run(fields=fields)
        return True
