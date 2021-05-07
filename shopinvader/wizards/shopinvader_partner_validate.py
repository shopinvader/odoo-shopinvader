# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopinvaderPartnerValidate(models.TransientModel):
    """Wizard used to validate customers.
    """

    _name = "shopinvader.partner.validate"
    _description = "Shopinvader partner validate"

    shopinvader_partner_ids = fields.Many2many(
        string="Invader Partners",
        comodel_name="shopinvader.partner",
        default=lambda self: self._default_shopinvader_partner_ids(),
    )
    next_state = fields.Selection(
        string="Action",
        selection=[
            ("active", "Activate"),
            ("inactive", "Inactivate"),
            ("pending", "Make pending"),
        ],
        default="active",
    )

    def _default_shopinvader_partner_ids(self):
        return self.env.context.get("active_ids")

    def action_apply(self):
        self.ensure_one()
        records = self.shopinvader_partner_ids.filtered_domain(
            [("state", "!=", self.next_state)]
        )
        records.write({"state": self.next_state})
        for record in records:
            record._event("on_shopinvader_validate").notify(record)
        return {"type": "ir.actions.act_window_close"}
