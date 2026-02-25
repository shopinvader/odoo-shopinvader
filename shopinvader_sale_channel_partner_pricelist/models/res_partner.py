# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        rv = super().create(vals_list)
        if self.env.context.get("sale_channel_id"):
            sale_channel = self.env["sale.channel"].browse(
                self.env.context["sale_channel_id"]
            )
            if sale_channel.partner_pricelist_id:
                rv.write(
                    {"property_product_pricelist": sale_channel.partner_pricelist_id.id}
                )

        return rv
