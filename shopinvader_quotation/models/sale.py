# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    typology = fields.Selection(selection_add=[("quotation", "Quotation")])
    shopinvader_state = fields.Selection(
        selection_add=[
            ("estimating", "Estimating Quotation"),
            ("estimated", "Estimated Quotation"),
        ]
    )

    @api.depends("state", "typology")
    def _compute_shopinvader_state(self):
        super()._compute_shopinvader_state()

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.typology == "quotation" and self.state == "draft":
            return "estimating"
        if self.typology == "quotation" and self.state == "sent":
            return "estimated"
        return super()._get_shopinvader_state()

    def action_request_quotation(self):
        for cart in self:
            if cart.state == "draft" and cart.typology == "cart":
                cart.typology = "quotation"
                if cart.shopinvader_backend_id:
                    cart.shopinvader_backend_id._send_notification(
                        "quotation_request", cart
                    )
            else:
                raise UserError(
                    _(
                        "Impossible to create quotation the"
                        "order is in the wrong state"
                    )
                )
        return True
