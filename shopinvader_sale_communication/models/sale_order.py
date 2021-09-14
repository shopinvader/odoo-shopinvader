# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_communication_id = fields.Many2one(
        comodel_name="sale.communication", string="Sale Communication Template"
    )
    online_information_for_customer = fields.Html(
        help="Fill in this field to provide your customer more information "
        "on his online account"
    )
    online_information_request = fields.Text(
        help="This field is filled by the customer to request information",
        readonly=True,
    )

    @api.onchange("sale_communication_id")
    def _onchange_sale_communication_id(self):
        for sale in self:
            if sale.sale_communication_id:
                sale.online_information_for_customer = (
                    sale.sale_communication_id.description
                )
            else:
                sale.online_information_for_customer = False
