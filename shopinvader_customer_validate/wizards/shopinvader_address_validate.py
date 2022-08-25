# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ShopinvaderAddressValidate(models.TransientModel):
    """
    Wizard used to validate customers' addresses for a given backend.
    """

    _name = "shopinvader.address.validate"
    _description = "Shopinvader address validate"

    backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        string="ShopInvader Backend",
        compute="_compute_valid_backend_ids",
        compute_sudo=True,
        store=True,
        readonly=False,
    )
    partner_ids = fields.Many2many(
        string="Addresses",
        comodel_name="res.partner",
        default=lambda self: self._default_partner_ids(),
        required=True,
    )
    valid_backend_ids = fields.Many2many(
        comodel_name="shopinvader.backend",
        compute="_compute_valid_backend_ids",
        compute_sudo=True,
    )
    display_warning = fields.Boolean(
        compute="_compute_valid_backend_ids",
        compute_sudo=True,
    )
    next_state = fields.Selection(
        string="Action",
        selection=[("active", "Activate"), ("inactive", "Inactivate")],
        default="active",
    )

    def _default_partner_ids(self):
        return self.env.context.get("active_ids")

    @api.constrains("partner_ids")
    def _check_partners(self):
        for rec in self:
            if not rec._get_valid_backends():
                raise exceptions.UserError(rec._msg_partner_must_have_binding)

    @api.constrains("backend_id")
    def _check_backend(self):
        for rec in self:
            if not rec.backend_id:
                raise exceptions.UserError(rec._msg_must_select_one_backend)
            valid = rec._get_valid_backends()
            if rec.backend_id not in valid:
                raise exceptions.UserError(rec._msg_must_select_valid_backend)

    @api.depends("partner_ids")
    def _compute_valid_backend_ids(self):
        for rec in self:
            valid = rec._get_valid_backends()
            rec.valid_backend_ids = valid
            rec.display_warning = len(valid) > 1
            if not rec.backend_id and len(valid) == 1:
                # set default
                rec.backend_id = valid

    def _get_valid_backends(self):
        """Get valid backends from partner's hierarchy."""
        return self.partner_ids._get_valid_backends()

    @property
    def _msg_must_select_one_backend(self):
        return _("You must select a backend")

    @property
    def _msg_must_select_valid_backend(self):
        return _("You must select a valid backend. Valid: %s") % ", ".join(
            self.valid_backend_ids.mapped("name")
        )

    @property
    def _msg_partner_must_have_binding(self):
        return _("Selected partners must have at least a binding")

    def action_apply(self):
        self.ensure_one()
        self._check_backend()
        self._action_apply()
        return {"type": "ir.actions.act_window_close"}

    def _action_apply(self):
        active = self.next_state == "active"
        records = self.partner_ids.filtered_domain(
            [("is_shopinvader_active", "!=", active)]
        )
        records.write({"is_shopinvader_active": active})
        if active:
            for record in records:
                if self.backend_id in record._get_valid_backends():
                    self._notify_validate("on_shopinvader_validate", record)

    def _notify_validate(self, event_name, record):
        record._event(event_name).notify(record, self.backend_id)
