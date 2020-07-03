# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class ShopinvaderSiteExportMapper(Component):
    _inherit = "shopinvader.site.export.mapper"
    _usage = "export.mapper"

    @mapping
    @changed_by("allowed_country_ids", "allowed_country_state_ids")
    def country(self, record):
        # Overwrite method to nest available states on each available country
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            for country in record.with_context(
                lang=lang.code
            ).allowed_country_ids:
                states = []
                for state in record.allowed_country_state_ids.filtered(
                    lambda x: x.country_id == country
                ):
                    states.append(
                        {
                            "name": state.name,
                            "id": state.id,
                            "code": state.code,
                        }
                    )
                res[lang.code[0:2]].append(
                    {"name": country.name, "id": country.id, "states": states}
                )
        return {"available_countries": res}
