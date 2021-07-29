# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _inherit = "shopinvader.partner.export.mapper"

    @mapping
    def password(self, record):
        # The pwd will be hashed by Locomotive
        return {"password": record.password}
