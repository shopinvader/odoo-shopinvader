# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.addons.component.core import Component


class ClientDeleter(Component):
    _name = "shopinvader.client.deleter"
    _inherit = ["shopinvader.client.connector", "base.deleter"]
    _usage = "record.exporter.deleter"

    def run(self, external_id):
        """ Run the synchronization, delete the record on client
        :param external_id: identifier of the record to delete
        """
        self.backend_adapter.delete(external_id)
        return _("Record %s deleted on client") % (external_id,)
