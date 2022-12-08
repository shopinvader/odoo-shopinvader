# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    typology = fields.Selection([("sale", "Sale"), ("cart", "Cart")], default="sale")

    def action_confirm_cart(self):
        for record in self:
            if record.typology == "sale":
                # cart is already confirmed
                continue
            record.write({"typology": "sale"})
        return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for record in self:
            if record.state != "draft" and record.typology != "sale":
                record.typology = "sale"
        return res
