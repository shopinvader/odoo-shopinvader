# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    def _compute_shopinvader_state_depends(self):
        return super()._compute_shopinvader_state_depends() + ("quotation_state",)

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.quotation_state == "customer_request":
            return "estimating"
        if self.quotation_state == "waiting_acceptation":
            return "estimated"
        return super()._get_shopinvader_state()
