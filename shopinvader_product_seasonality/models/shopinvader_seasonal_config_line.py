# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderSeasonalConfigLine(models.Model):
    _name = "shopinvader.seasonal.config.line"
    _inherit = ["shopinvader.binding"]
    _inherits = {"seasonal.config.line": "record_id"}
    _description = "Shopinvader Seasonal Config Binding"

    record_id = fields.Many2one(
        comodel_name="seasonal.config.line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    display_name = fields.Char(related="record_id.display_name")
    product_ids = Serialized(
        default=[],
        compute="_compute_product_ids",
    )
    weekdays = Serialized(
        default=[],
        compute="_compute_weekdays",
        help="List of weekdays numbers (zero-based)",
    )
    # TODO: decide what to do w/ this
    active = fields.Boolean()

    @api.depends("product_template_id.product_variant_ids", "product_id")
    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = (
                # Either specific product ID or all variants for the template
                rec.product_id.ids
                or rec.product_template_id.product_variant_ids.ids
            )

    def _compute_weekdays_depends(self):
        return (
            "record_id.monday",
            "record_id.tuesday",
            "record_id.wednesday",
            "record_id.thursday",
            "record_id.friday",
            "record_id.saturday",
            "record_id.sunday",
        )

    @api.depends(lambda self: self._compute_weekdays_depends())
    def _compute_weekdays(self):
        """Compute the list of weekdays as a list of integers

        The result is a list of zero-based numbers for each applicable weekday.

        Example result:

            .. code-block:: python

            # 0 = Sunday, 1 = Monday, ..., 6 = Saturday
            [1, 2, 3, 4, 5]
        """
        weekday_fields = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        values = {x["id"]: x for x in self.read(weekday_fields)}
        for rec in self:
            weekdays = []
            for i, day in enumerate(weekday_fields):
                if values[rec.id].get(day):
                    weekdays.append(i)
            rec.weekdays = weekdays

    def get_shop_data(self):
        """Return data for the shop."""
        return self._get_shop_data()

    def _get_shop_data_exporter(self):
        exporter_xid = "shopinvader_product_seasonality.ir_exp_seasonal_config_line"
        return self.env.ref(exporter_xid)

    def _get_shop_data(self):
        """Compute shop data base_jsonify parser."""
        exporter = self._get_shop_data_exporter()
        return self.jsonify(exporter.get_json_parser(), one=True)

    def create_bindings_from_lines(self, config_lines):
        to_create = []
        by_backend = defaultdict(config_lines.browse)
        for line in config_lines:
            backends = (
                line.product_id.shopinvader_bind_ids.backend_id
                or line.product_template_id.shopinvader_bind_ids.backend_id
            )
            for backend_id in set(backends.ids):
                by_backend[backend_id] += line

        for backend_id, lines in by_backend.items():
            existing = self.search(
                [
                    ("record_id", "in", lines.ids),
                    ("backend_id", "=", backend_id),
                ]
            )
            missing = lines - existing.record_id
            for line in missing:
                to_create.append(self._prepare_config_line_values(backend_id, line))

        if to_create:
            return self.create(to_create)
        return self.browse()

    def _prepare_config_line_values(self, backend_id, line):
        return {
            "backend_id": backend_id,
            "record_id": line.id,
        }
