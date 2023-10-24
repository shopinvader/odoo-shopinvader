# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except (ImportError, IOError) as err:
    _logger.debug(err)


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

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

    def _default_stock_field_id(self):
        return self.env.ref("stock.field_product_product__qty_available")

    def _default_warehouse_ids(self):
        return self.env["stock.warehouse"].search([], limit=1)

    def _get_warehouse_list_for_export(self):
        """Return the list of warehouse what will be used for exporting the
        stock level. A global key "global" is added with the list of all
        warehouse ids
        :return: dict with warehouse code as key and warehouse_ids as value"""
        self.ensure_one()
        result = {"global": self.warehouse_ids.ids}
        if len(self.warehouse_ids) > 1:
            for warehouse in self.warehouse_ids:
                result[slugify(warehouse.code)] = [warehouse.id]
        return result
