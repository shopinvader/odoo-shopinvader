# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_program_timezone(self):
        # Workaround security issue
        if self.env.user.has_group(
            "shopinvader_api_security_sale.shopinvader_sale_user_group"
        ):
            sudo_tz = self.company_id.sudo().partner_id.tz
            if sudo_tz:
                return sudo_tz
        return super()._get_program_timezone()
