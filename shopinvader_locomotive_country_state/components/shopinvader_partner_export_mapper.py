# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class ShopinvaderSiteExportMapper(Component):
    _inherit = "shopinvader.site.export.mapper"
    _usage = "export.mapper"

    @mapping
    @changed_by("allowed_country_state_ids")
    def state(self, record):
        return {
            "available_country_states": self._m2m_to_external(
                record,
                "allowed_country_state_ids",
                ["id", "name", ("country_id", ["id"])],
            )
        }
