# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models

from .shopinvader_partner import STATE_ACTIVE, STATE_PENDING


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Set inactive by default.
    # Would be nice to be able to do it based on backend settings
    # but addresses are not bound to a backend.
    is_shopinvader_active = fields.Boolean(default=False)
    has_shopinvader_user_active = fields.Boolean(
        help="This partner has at least a Shopinvader active user.",
        compute="_compute_has_shopinvader_user",
        compute_sudo=True,
        store=True,
    )
    has_shopinvader_user_to_validate = fields.Boolean(
        help="This partner has at least a Shopinvader user to be validated.",
        compute="_compute_has_shopinvader_user",
        compute_sudo=True,
        store=True,
    )
    has_shopinvader_address_to_validate = fields.Boolean(
        help="This partner has at least an address to validate for Shopinvader.",
        compute="_compute_has_shopinvader_address_to_validate",
        compute_sudo=True,
    )
    display_validate_address = fields.Boolean(
        help="Tech field to be used in views to display/hide validate action.",
        compute="_compute_display_flags",
        compute_sudo=True,
    )

    @api.depends("shopinvader_bind_ids.state")
    def _compute_has_shopinvader_user(self):
        super()._compute_has_shopinvader_user()
        for record in self:
            record.has_shopinvader_user_active = any(
                record.shopinvader_bind_ids.filtered(lambda x: x.state == STATE_ACTIVE)
            )
            record.has_shopinvader_user_to_validate = any(
                record.shopinvader_bind_ids.filtered(lambda x: x.state == STATE_PENDING)
            )

    @api.depends(
        "has_shopinvader_user_active",
        "child_ids.address_type",
        "child_ids.is_shopinvader_active",
    )
    def _compute_has_shopinvader_address_to_validate(self):
        addresses_to_validate = self.read_group(
            [
                ("parent_id", "child_of", self.ids),
                ("parent_id.has_shopinvader_user_active", "=", True),
                ("shopinvader_bind_ids", "=", False),
                ("address_type", "=", "address"),
                ("is_shopinvader_active", "=", False),
            ],
            ["parent_id"],
            ["parent_id"],
        )
        by_parent = {
            x["parent_id"][0]: x["parent_id_count"]
            for x in addresses_to_validate
            if x["parent_id"]
        }
        for record in self:
            record.has_shopinvader_address_to_validate = bool(by_parent.get(record.id))

    def _compute_display_flags(self):
        for record in self:
            record.display_validate_address = record._display_validate_address()

    def _display_validate_address(self):
        if self.has_shopinvader_user:
            # this is a user, no address
            return False
        has_parent = self._get_has_shopinvader_parent()
        return has_parent and self.address_type == "address"

    def _get_has_shopinvader_parent(self):
        has_shopinvader_user = self.parent_has_shopinvader_user
        if has_shopinvader_user:
            return True
        parent = self.parent_id
        while parent and not has_shopinvader_user:
            parent = parent.parent_id
            has_shopinvader_user = parent.parent_has_shopinvader_user
        return has_shopinvader_user

    def action_shopinvader_validate_customer(self):
        return self.shopinvader_bind_ids.action_shopinvader_validate()

    def action_shopinvader_validate_address(self):
        wiz = self._get_shopinvader_validate_address_wizard()
        action = self.env.ref(
            "shopinvader_customer_validate.shopinvader_address_validate_act_window"
        )
        action_data = action.read()[0]
        action_data["res_id"] = wiz.id
        return action_data

    def _get_shopinvader_validate_address_wizard(self, **kw):
        ids = self.ids
        if self.env.context.get("shopinvader__validate_customer_children"):
            ids = self.child_ids.filtered_domain(
                [
                    ("has_shopinvader_user", "=", False),
                    ("address_type", "=", "address"),
                    ("is_shopinvader_active", "=", False),
                ]
            ).ids
        vals = dict(partner_ids=ids, **kw)
        return self.env["shopinvader.address.validate"].create(vals)
