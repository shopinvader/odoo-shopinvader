# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.component.core import Component


class LocomotiveDeleter(Component):
    _name = "locomotive.deleter"
    _inherit = ["base.locomotive.connector", "base.deleter"]
    _usage = "record.exporter.deleter"

    def run(self, external_id):
        """Run the synchronization, delete the record on Lcomotive
        :param external_id: identifier of the record to delete
        """
        self.backend_adapter.delete(external_id)
        return _("Record %s deleted on Locomotive") % (external_id,)
