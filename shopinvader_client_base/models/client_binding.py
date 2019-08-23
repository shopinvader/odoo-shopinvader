# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.addons.queue_job.job import job, related_action


class ClientBinding(models.AbstractModel):
    _name = "shopinvader.client.binding"
    # Your model must also have _inherit = 'shopinvader.binding'

    @job(default_channel="root.shopinvader")
    @related_action(action="related_action_unwrap_binding")
    @api.multi
    def export_record(self, _fields=None):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self)

    @job(default_channel="root.shopinvader")
    @related_action(action="related_action_unwrap_binding")
    @api.model
    def export_delete_record(self, backend, external_id):
        with backend.work_on(self._name) as work:
            deleter = work.component(usage="record.exporter.deleter")
            return deleter.run(external_id)

    _sql_constraints = [
        (
            "shopinvader_client_uniq",
            "unique(backend_id, external_id)",
            "A binding already exists with the same client ID.",
        )
    ]
