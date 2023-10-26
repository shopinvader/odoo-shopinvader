# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SeBackend(models.Model):
    _inherit = "se.backend"

    # NOTE: this field right now has no effect on qty sync.
    # It's here to allow extending modules to define their own policies.
    # See example in `shopinvader_product_stock_state`.
    stock_level_config = fields.Selection(
        selection="_selection_stock_level_config",
        default="only_qty",
        required=True,
        help="Define stock level export policy",
    )
    show_stock_level_config = fields.Boolean(compute="_compute_show_stock_level_config")

    def _selection_stock_level_config(self):
        return [("only_qty", "Only Quantity")]

    @api.depends("index_ids", "index_ids.model_id")
    def _compute_show_stock_level_config(self):
        product_model_id = (
            self.env["ir.model"].search([("model", "=", "product.product")]).id
        )
        for backend in self:
            backend.show_stock_level_config = (
                product_model_id in backend.index_ids.mapped("model_id").ids
            )
