# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions, fields, models


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

    def action_apply(self):
        """
        Bind selected partners
        :return: dict
        """
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
                bind_values = {"backend_id": backend.id}
                record.partner_id.write(
                    {"shopinvader_bind_ids": [(0, False, bind_values)]}
                )
        return {}
