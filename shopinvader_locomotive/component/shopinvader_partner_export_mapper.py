# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _name = "shopinvader.partner.export.mapper"
    _inherit = ["locomotive.export.mapper"]
    _usage = "export.mapper"

    direct = [("email", "email")]

    @mapping
    def role(self, record):
        return {"role": record.role}

    @mapping
    def name(self, record):
        # we do not use a direct mapping to simplify the inherit
        return {"name": record.name}
