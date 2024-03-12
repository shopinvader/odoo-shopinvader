# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, MissingError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    unit_profile = fields.Selection(
        selection=[
            ("unit", "Unit"),
            ("manager", "Unit Manager"),
            ("collaborator", "Unit Collaborator"),
        ],
        string="Unit Profile",
        required=False,
    )

    unit_id = fields.Many2one("res.partner", related="parent_id", string="Unit")

    manager_ids = fields.One2many(
        "res.partner", "unit_id", domain=[("unit_profile", "=", "manager")]
    )
    collaborator_ids = fields.One2many(
        "res.partner", "unit_id", domain=[("unit_profile", "=", "collaborator")]
    )
    member_ids = fields.One2many(
        "res.partner",
        "unit_id",
        domain=[("unit_profile", "in", ["manager", "collaborator"])],
    )

    def _ensure_manager(self):
        """Ensure the partner is a manager."""
        if not self.unit_profile == "manager":
            raise AccessError(_("Only a manager can perform this action."))

    def _ensure_same_unit(self, member):
        """Ensure the member is in the same unit."""
        if not member or member.unit_id != self.unit_id:
            raise MissingError(_("Member not found"))

    @api.model
    def _get_shopinvader_unit_members(self):
        self._ensure_manager()
        return self.unit_id.member_ids

    @api.model
    def _get_shopinvader_unit_member(self, id):
        self._ensure_manager()
        member = self.browse(id)
        self._ensure_same_unit(member)
        return member

    @api.model
    def _create_shopinvader_unit_member(self, vals):
        self._ensure_manager()
        # FIXME:
        vals[self._fields["unit_id"].related[0]] = self.unit_id.id

        if "unit_profile" not in vals:
            vals["unit_profile"] = "collaborator"
        if vals["unit_profile"] not in dict(self._fields["unit_profile"].selection):
            raise ValidationError(_("Invalid member type"))
        if vals["unit_profile"] not in ["collaborator", "manager"]:
            raise AccessError(_("Only collaborators and managers can be created"))
        return self.create(vals)

    @api.model
    def _update_shopinvader_unit_member(self, id, vals):
        self._ensure_manager()
        member = self.browse(id)
        self._ensure_same_unit(member)
        if member.unit_profile not in ["collaborator", "manager"]:
            raise AccessError(_("Cannot perform this action on this member"))
        member.write(vals)
        return member

    @api.model
    def _delete_shopinvader_unit_member(self, id):
        self._ensure_manager()
        member = self.browse(id)
        self._ensure_same_unit(member)
        if member.unit_profile not in ["collaborator", "manager"]:
            raise AccessError(_("Cannot perform this action on this member"))
        member.active = False
        return member
