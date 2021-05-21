# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SeasonalConfigLineEventListener(Component):
    _name = "seasonal.config.line.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["seasonal.config.line"]

    @skip_if(lambda self, record, **kw: not self._product_is_bound(record, **kw))
    def on_record_create(self, record, fields=None):
        self._create_config_line_bindings_if_missing(record)

    def _product_is_bound(self, record, **kw):
        """Check if related product is bound to the shop."""
        return any(
            (
                record.product_id.shopinvader_bind_ids,
                record.product_template_id.shopinvader_bind_ids,
            )
        )

    def _create_config_line_bindings_if_missing(self, seasonal_config_line):
        self.env[
            "shopinvader.seasonal.config.line"
        ].with_delay().create_bindings_from_lines(seasonal_config_line)

    def on_record_write(self, record, fields=None):
        if not self._product_is_bound(record) and record.shopinvader_bind_ids:
            self._handle_product_not_bound_anymore(record)
        else:
            self._update_config_line_bindings(record)

    def _fields_triggering_update(self):
        return [
            "seasonal_config_id",
            "product_template_id",
            "product_id",
            "date_start",
            "date_end",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

    def _needs_update(self, fields=None):
        fields = fields or []
        check_fields = self._fields_triggering_update()
        return any(field in check_fields for field in fields)

    def _handle_product_not_bound_anymore(self, record):
        record.shopinvader_bind_ids.filtered(lambda x: x.active).write(
            {"active": False}
        )

    def _update_config_line_bindings(self, seasonal_config_lines):
        # Normally values will get recomputed automatically.
        # Hook here to do what you want.
        pass
