# wizards/sale_order_confirm_warning_wizard.py
from odoo import fields, models


class SaleOrderConfirmWarningWizard(models.TransientModel):
    _name = "sale.order.confirm.warning.wizard"
    _description = "Sale Order Confirmation Warning Wizard"

    sale_order_ids = fields.Many2many("sale.order", string="Sale Orders", required=True)
    message = fields.Char(readonly=True)

    def confirm_and_proceed(self):
        for order in self.sale_order_ids:
            order.action_customer_accept_quotation()
        self.sale_order_ids.with_context(
            use_quotation_confirm_wizard=False
        ).action_confirm()
        return {"type": "ir.actions.act_window_close"}
