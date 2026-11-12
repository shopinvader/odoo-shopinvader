# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cart_request_quotation(self):
        if any(rec.state != "draft" or rec.typology != "cart" for rec in self):
            raise UserError(
                self.env._(
                    "Only orders of cart typology in draft state "
                    "can be converted to quotation"
                )
            )
        self.write({"use_customer_quotation_workflow": True})
        self.action_customer_request_quotation()
        return True
