# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderPartnerBinding(models.TransientModel):
    """
    Wizard used to bind manually some partners on shopinvader backends
    """

    _name = "shopinvader.partner.binding"
    _description = "Shopinvader partner binding"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        string="Shopinvader backend",
        required=True,
        ondelete="cascade",
    )
    binding_lines = fields.One2many(
        comodel_name="shopinvader.partner.binding.line",
        inverse_name="shopinvader_partner_binding_id",
        string="Lines",
    )

    @api.model
    def default_get(self, fields_list):
        """
        Inherit the default_get to auto-fill the backend if only 1 is found
        :param fields_list: list of str
        :return: dict
        """
        result = super(ShopinvaderPartnerBinding, self).default_get(fields_list)
        # Auto fill the backend if we have only 1 backend found
        backend = self.shopinvader_backend_id.search([], limit=2)
        if len(backend) == 1:
            result.update({"shopinvader_backend_id": backend.id})
        return result

    @api.onchange("shopinvader_backend_id")
    def _onchange_shopinvader_backend_id(self):
        """
        Onchange for the shopinvader_backend_id field.
        Auto fill some info based on active_ids and selected backend.
        :return:
        """
        if self.env.context.get("active_model") == "res.partner":
            partner_ids = self.env.context.get("active_ids", [])
            lines = [(6, False, [])]
            for partner in self.env["res.partner"].browse(partner_ids):
                shopinv_partner = partner.shopinvader_bind_ids.filtered(
                    lambda x, b=self.shopinvader_backend_id: x.backend_id == b
                )
                if shopinv_partner:
                    # If the user is already binded, ignore it
                    continue
                values = {"partner_id": partner.id, "bind": False}
                lines.append((0, False, values))
        self.binding_lines = lines

    def action_apply(self):
        """
        Apply binding
        :return:
        """
        self.ensure_one()
        self.binding_lines.action_apply()
        return {"type": "ir.actions.act_window_close"}
