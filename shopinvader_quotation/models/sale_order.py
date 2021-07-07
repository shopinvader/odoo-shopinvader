# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    typology = fields.Selection(
        selection_add=[("quotation", "Quotation")],
        ondelete={"quotation": "cascade"},
    )
    shopinvader_state = fields.Selection(
        selection_add=[
            ("estimating", "Estimating Quotation"),
            ("estimated", "Estimated Quotation"),
        ],
        ondelete={
            "estimating": "cascade",
            "estimated": "cascade",
        },
    )

    @api.depends("state", "typology")
    def _compute_shopinvader_state(self):
        # Overload to add typology in api.depends
        return super()._compute_shopinvader_state()

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.typology == "quotation" and self.state == "draft":
            return "estimating"
        if self.typology == "quotation" and self.state == "sent":
            return "estimated"
        return super()._get_shopinvader_state()

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
            if rec.shopinvader_backend_id:
                rec.shopinvader_backend_id._send_notification("quotation_request", rec)
        return True
