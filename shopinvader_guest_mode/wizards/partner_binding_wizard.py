# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShopinvaderPartnerBinding(models.TransientModel):

    _inherit = "shopinvader.partner.binding"

    @api.multi
    @api.onchange("shopinvader_backend_id")
    def _onchange_shopinvader_backend_id(self):
        """
        Onchange for the shopinvader_backend_id field.
        Auto fill some info based on active_ids and selected backend.
        :return:
        """
        super(
            ShopinvaderPartnerBinding, self
        )._onchange_shopinvader_backend_id()
        if self.env.context.get("active_model") == "res.partner":
            partner_ids = self.env.context.get("active_ids", [])
            lines = []
            for partner in self.env["res.partner"].browse(partner_ids):
                shopinv_partner = partner.shopinvader_bind_ids.filtered(
                    lambda x, b=self.shopinvader_backend_id: x.backend_id == b
                    and x.is_guest
                )
                if shopinv_partner:
                    line = self.binding_lines.filtered(
                        lambda l: l.partner_id == shopinv_partner.partner_id
                    )
                    if not line:
                        values = {
                            "partner_id": partner.id,
                            "bind": False,
                            "is_guest": True,
                        }
                        lines.append((0, False, values))
                    else:
                        # We found a partner that is guest
                        line.udpate({"is_guest": True})
            if lines:
                self.binding_lines = lines
