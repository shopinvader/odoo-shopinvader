# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import UserError


class ClientAdapter(AbstractComponent):
    """Generic client adapter.

    You are supposed to implement CRUD methods in your extension.
    """
    _name = "shopinvader.client.adapter"
    _inherit = ["base.backend.adapter.crud", "shopinvader.client.connector"]

    def __init__(self, work_context):
        super().__init__(work_context)
        self.backend = self.collection
        self.client_data = self.backend.client_data


# TODO:  probably useless
class ClientBackendAdapter(AbstractComponent):
    _name = "shopinvader.backend.client.adapter"
    _apply_on = "shopinvader.backend"

    def _site_not_found(self, handle):
        raise UserError(_("No site was found for the handle %s") % handle)
