# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ShopinvaderPartnerBindingLine(models.TransientModel):
    """
    Wizard lines used to bind manually some partners on shopinvader backends
    """

    _name = "shopinvader.partner.binding.line"
    _description = "Shopinvader partner binding line"

    shopinvader_partner_binding_id = fields.Many2one(
        comodel_name="shopinvader.partner.binding",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    email = fields.Char(
        related="partner_id.email", required=True, readonly=True
    )
    bind = fields.Boolean(
        help="Tick to bind the partner to the backend. Untick to unbind it."
    )

    @api.multi
    def action_apply(self):
        """
        Bind selected partners
        :return: dict
        """
        shopinvader_partner_obj = self.env["shopinvader.partner"]
        if self.filtered(lambda r: not r.bind):
            message = _(
                "The unbind is not implemented.\n"
                "If you want to continue, please delete lines where "
                "the bind field is not ticked."
            )
            raise exceptions.UserError(message)
        for record in self.filtered(lambda r: r.bind):
            backend = (
                record.shopinvader_partner_binding_id.shopinvader_backend_id
            )
            # Ensure the binding doesn't exist yet
            partner_binding = record.partner_id.shopinvader_bind_ids.filtered(
                lambda x, b=backend: x.backend_id == b
            )
            if not partner_binding:
                bind_values = {
                    "backend_id": backend.id,
                    "record_id": record.partner_id.id,
                }
                # Locomotive doesn't work with uppercase.
                # And we have to do the write before the binding
                email_lower = (record.partner_id.email or "").lower()
                # Do the update only if necessary
                if record.partner_id.email != email_lower:
                    bind_values.update({"email": email_lower})

                shopinvader_partner_obj.create(bind_values)
        return {}
