# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class LocomotiveBinding(models.AbstractModel):
    _name = "locomotive.binding"
    _description = "Locomotive Binding"
    # Your model must also have _inherit = 'shopinvader.binding'

    def export_record(self, _fields=None):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self.sudo())

    def export_delete_record(self, backend, external_id):
        with backend.work_on(self._name) as work:
            deleter = work.component(usage="record.exporter.deleter")
            return deleter.run(external_id)

    _sql_constraints = [
        (
            "locomotive_uniq",
            "unique(backend_id, external_id)",
            "A binding already exists with the same Locomotive ID.",
        )
    ]
