# Copyright 2021 ForgeFlow S.A. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _inherit = "shopinvader.partner.export.mapper"

    @mapping
    def can_manage_users(self, record):
        return {"can_manage_users": record.can_manage_users}
