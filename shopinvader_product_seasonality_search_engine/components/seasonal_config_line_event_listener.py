# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class SeasonalConfigLineEventListener(Component):
    _inherit = "seasonal.config.line.event.listener"

    def _update_config_line_bindings(self, seasonal_config_lines):
        super()._update_config_line_bindings(seasonal_config_lines)
        bindings = seasonal_config_lines.mapped("shopinvader_bind_ids")
        bindings.jobify_recompute_json()
