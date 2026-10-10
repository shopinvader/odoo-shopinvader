# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderApiSaleSaleLineRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_sale.sale_line_router.helper"

    def _get_domain_adapter(self):
        return [
            "|",
            ("request_partner_id", "=", self.partner.id),
            "&",
            ("order_id.partner_id", "=", self.partner.id),
            "|",
            ("order_id.typology", "=", "sale"),
            ("order_id.typology", "=", "request"),
        ]
