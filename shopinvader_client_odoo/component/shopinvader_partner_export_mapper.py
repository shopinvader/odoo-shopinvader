# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _name = "odoo.partner.export.mapper"
    _inherit = ["shopinvader.partner.export.mapper"]
    _usage = "export.mapper"
