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

    @api.constrains("unit_profile", "parent_id")
    def _check_unit_profile(self):
        if self.unit_profile:
            if self.unit_profile == "unit" and self.parent_id:
                raise ValidationError(_("A unit can't have a parent."))
            if self.unit_profile in ["manager", "collaborator"] and not self.parent_id:
                raise ValidationError(
                    _("A manager or a collaborator must have a parent unit.")
                )

    @api.model
    def _get_unit_members(self):
        self.ensure_one()
        if self.unit_profile != "unit":
            raise AccessError(_("This method is only available for units."))
        return self.search(
            [
                ("parent_id", "=", self.id),
                ("unit_profile", "in", ["manager", "collaborator"]),
            ]
        )

    @api.model
    def _get_unit_managers(self):
        self.ensure_one()
        if self.unit_profile != "unit":
            raise AccessError(_("This method is only available for units."))
        return self.search(
            [("parent_id", "=", self.id), ("unit_profile", "=", "manager")]
        )

    @api.model
    def _get_unit_collaborators(self):
        self.ensure_one()
        if self.unit_profile != "unit":
            raise AccessError(_("This method is only available for units."))
        return self.search(
            [("parent_id", "=", self.id), ("unit_profile", "=", "collaborator")]
        )

    @api.model
    def _get_unit(self):
        self.ensure_one()
        if self.unit_profile not in ["manager", "collaborator"]:
            raise AccessError(
                _("This method is only available for managers and collaborators.")
            )
        return self.parent_id

    def _ensure_manager(self):
        """Ensure the partner is a manager."""
        if not self.unit_profile == "manager":
            raise AccessError(_("Only a manager can perform this action."))

    def _ensure_same_unit(self, member):
        """Ensure the member is in the same unit."""
        if not member or member._get_unit() != self._get_unit():
            raise MissingError(_("Member not found"))

    @api.model
    def _get_shopinvader_unit_members(self):
        self._ensure_manager()
        unit = self._get_unit()
        return unit._get_unit_members()

    @api.model
    def _get_shopinvader_unit_member(self, id):
        self._ensure_manager()
        member = self.browse(id)
        self._ensure_same_unit(member)
        return member

    @api.model
    def _create_shopinvader_unit_member(self, vals):
        self._ensure_manager()
        vals["parent_id"] = self._get_unit().id
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
