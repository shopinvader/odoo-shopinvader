# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerAdapter(AbstractComponent):
    """Generic adapter for partner client content."""
    _name = "shopinvader.partner.adapter"
    _apply_on = "shopinvader.partner"


class ShopinvaderPartnerExportMapper(AbstractComponent):
    """Generic adapter for partner client content."""
    _name = "shopinvader.partner.export.mapper"
    _inherit = "shopinvader.client.export.mapper"
    _usage = "export.mapper"

    direct = [("email", "email")]

    @mapping
    def name(self, record):
        # we do not use a direct mapping to simplify the inherit
        return {"name": record.name}
