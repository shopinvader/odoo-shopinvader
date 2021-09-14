from odoo import fields, models


class SaleCommunication(models.Model):
    _name = "sale.communication"
    _description = "Sale Communication"

    name = fields.Char(required=True)
    description = fields.Html()
    active = fields.Boolean(default=True)
    order_ids = fields.One2many(
        comodel_name="sale.order", inverse_name="sale_communication_id"
    )

    def write(self, vals):
        res = super().write(vals)
        if "description" in vals:
            self.order_ids._onchange_sale_communication_id()
        return res
