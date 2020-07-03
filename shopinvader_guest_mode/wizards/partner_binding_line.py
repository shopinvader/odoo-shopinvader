# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderPartnerBindingLine(models.TransientModel):

    _inherit = "shopinvader.partner.binding.line"

    is_guest = fields.Boolean()

    @api.multi
    def action_apply(self):
        """
        Bound partners as guest should be moved to real shopinvader partners
        by setting 'is_guest' to False
        :return: dict
        """
        res = super(ShopinvaderPartnerBindingLine, self).action_apply()
        for record in self.filtered(lambda r: r.bind and r.is_guest):
            backend = (
                record.shopinvader_partner_binding_id.shopinvader_backend_id
            )
            partner_binding = record.partner_id.shopinvader_bind_ids.filtered(
                lambda x, b=backend: x.backend_id == b
            )
            if partner_binding:
                partner_binding.write({"is_guest": False})

        return res
