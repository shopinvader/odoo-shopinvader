# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except (ImportError, IOError) as err:
    _logger.debug(err)


class SeIndex(models.Model):

    _inherit = "se.index"

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        default=lambda self: self._default_warehouse_ids(),
        required=True,
    )
    product_stock_field_id = fields.Many2one(
        "ir.model.fields",
        "Product stock field",
        domain=[
            ("ttype", "in", ["float", "integer"]),
            ("model", "in", ["product.product", "product.template"]),
        ],
        help="Field used to have the current stock of a product.product",
        default=lambda self: self._default_stock_field_id(),
    )
    synchronize_stock = fields.Selection(
        [("immediatly", "Immediatly"), ("in_batch", "In Batch")],
        default="immediatly",
        help=(
            "If immediatly the stock will be exported after each "
            'modification. If "In batch" the stock exported every X time '
            "depending on the cron configuration"
        ),
    )
    # NOTE: this field right now has no effect on qty sync.
    # It's here to allow extending modules to define their own policies.
    # See example in `shopinvader_product_stock_state`.
    stock_level_config = fields.Selection(
        selection=lambda self: self.backend_id._selection_stock_level_config(),
        help="Define stock level export policy, "
        "keep empty to take configuration from the backend",
    )

    def _default_stock_field_id(self):
        return self.env.ref("stock.field_product_product__qty_available")

    def _default_warehouse_ids(self):
        return self.env["stock.warehouse"].search([], limit=1)

    def _get_stock_level_config(self):
        self.ensure_one()
        return self.stock_level_config or self.backend_id.stock_level_config

    def _get_warehouse_list_for_export(self):
        """Get list of warehouse to be used for exporting stock level.

        A global key "global" is added with the list of all warehouse ids.

        :return: dict with warehouse code as key and warehouse_ids as value"""
        self.ensure_one()
        result = {"global": self.warehouse_ids.ids}
        if len(self.warehouse_ids) > 1:
            for warehouse in self.warehouse_ids:
                result[self._make_warehouse_key(warehouse)] = [warehouse.id]
        return result

    def _make_warehouse_key(self, wh):
        return slugify(wh.code)
