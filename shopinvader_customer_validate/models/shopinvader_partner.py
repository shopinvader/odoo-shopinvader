# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models

STATE_ACTIVE = "active"
STATE_INACTIVE = "inactive"
STATE_PENDING = "pending"
ALL_STATES = (STATE_ACTIVE, STATE_INACTIVE, STATE_PENDING)


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    state = fields.Selection(
        selection="_selection_state",
        default=STATE_ACTIVE,
    )

    def _selection_state(self):
        return [
            (STATE_ACTIVE, "Active"),
            (STATE_INACTIVE, "Inactive"),
            (STATE_PENDING, "Pending"),
        ]

    def _compute_is_shopinvader_active_depends(self):
        return super()._compute_is_shopinvader_active_depends() + ("state",)

    def _is_shopinvader_user_active(self):
        return self.state == STATE_ACTIVE

    def action_shopinvader_validate(self):
        wiz = self._get_shopinvader_validate_wizard()
        action = self.env.ref(
            "shopinvader_customer_validate.shopinvader_partner_validate_act_window"
        )
        action_data = action.read()[0]
        action_data["res_id"] = wiz.id
        return action_data

    def _get_shopinvader_validate_wizard(self, **kw):
        vals = dict(shopinvader_partner_ids=self.ids, **kw)
        return self.env["shopinvader.partner.validate"].create(vals)
