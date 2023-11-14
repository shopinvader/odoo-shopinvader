# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    typology = fields.Selection(
        selection_add=[("quotation", "Quotation")],
        ondelete={"quotation": "cascade"},
    )
    available_for_quotation = fields.Boolean(compute="_compute_available_for_quotation")
    shop_only_quotation = fields.Boolean(compute="_compute_shop_only_quotation")

    def action_request_quotation(self):
        if any(rec.state != "draft" or rec.typology != "cart" for rec in self):
            raise UserError(
                _(
                    "Only orders of cart typology in draft state "
                    "can be converted to quotation"
                )
            )
        for rec in self:
            rec.typology = "quotation"
        return self

    def _compute_available_for_quotation(self):
        for record in self:
            record.available_for_quotation = True

    def _compute_shop_only_quotation(self):
        for record in self:
            record.shop_only_quotation = any(
                record.order_line.product_id.mapped("shop_only_quotation")
            )
