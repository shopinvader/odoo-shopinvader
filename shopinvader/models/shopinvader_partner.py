# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models

STATE_ACTIVE = "active"
STATE_INACTIVE = "inactive"
STATE_PENDING = "pending"
ALL_STATES = (STATE_ACTIVE, STATE_INACTIVE, STATE_PENDING)


class ShopinvaderPartner(models.Model):
    _name = "shopinvader.partner"
    _description = "Shopinvader Partner"
    _inherit = "shopinvader.binding"
    _inherits = {"res.partner": "record_id"}

    record_id = fields.Many2one(
        "res.partner", string="Partner", required=True, ondelete="restrict"
    )
    partner_email = fields.Char(
        related="record_id.email",
        required=True,
        store=True,
        string="Partner Email",
    )
    role = fields.Char(compute="_compute_role")
    state = fields.Selection(selection="_select_state", default=STATE_ACTIVE,)
    # Common interface to mimic the same behavior as res.partner.
    # On the binding we have a selection for the state
    # and we can set the value for each backend.
    # On addresses is relevant only if the record is enabled or not for the shop.
    # Having the same field on both models allows to use simple conditions to check.
    is_shopinvader_active = fields.Boolean(
        compute="_compute_is_shopinvader_active"
    )

    def _select_state(self):
        return [
            (STATE_ACTIVE, "Active"),
            (STATE_INACTIVE, "Inactive"),
            (STATE_PENDING, "Pending"),
        ]

    @api.depends("state")
    def _compute_is_shopinvader_active(self):
        for rec in self:
            rec.is_shopinvader_active = rec.state == STATE_ACTIVE

    _sql_constraints = [
        (
            "record_uniq",
            "unique(backend_id, record_id, partner_email)",
            "A partner can only have one binding by backend.",
        ),
        (
            "email_uniq",
            "unique(backend_id, partner_email)",
            "An email must be uniq per backend.",
        ),
    ]

    def _compute_role_depends(self):
        return ("backend_id", "backend_id.customer_default_role")

    @api.depends(lambda self: self._compute_role_depends())
    def _compute_role(self):
        for rec in self:
            rec.role = rec._get_role()

    def _get_role(self):
        return self.backend_id.customer_default_role

    @api.model
    def create(self, vals):
        vals = self._prepare_create_params(vals)
        return super(ShopinvaderPartner, self).create(vals)

    @api.model
    def _prepare_create_params(self, vals):
        # As we want to have a SQL contraint on customer email
        # we have to set it manually to avoid to raise the constraint
        # at the creation of the element
        if not vals.get("partner_email"):
            vals["partner_email"] = vals.get("email")
        if not vals.get("partner_email") and vals.get("record_id"):
            vals["partner_email"] = (
                self.env["res.partner"].browse(vals["record_id"]).email
            )
        if not vals.get("record_id"):
            vals["record_id"] = self._get_or_create_partner(vals).id
        return vals

    @api.model
    def _get_or_create_partner(self, vals):
        partner = self.env["res.partner"].browse()
        if partner._is_partner_duplicate_prevented():
            domain = self._get_unique_partner_domain(vals)
            partner = partner.search(domain, limit=1)
        if partner:
            # here we check if one of the given value is different than those
            # on partner. If true, we create a child partner to keep the
            # given informations
            if not self._is_same_partner_value(partner, vals):
                self._create_child_partner(partner, vals)
            return partner
        partner_values = vals.copy()
        keys = partner_values.keys()
        # Some fields are related to shopinvader.partner and doesn't exist
        # in res.partner
        values = {}
        for k in keys:
            if k in partner._fields:
                values.update({k: partner_values[k]})
        return partner.create(values)

    @api.model
    def _get_unique_partner_domain(self, vals):
        """ """
        email = vals["email"]
        return [("email", "=", email)]

    @api.model
    def _is_same_partner_value(self, partner, vals):
        """ we check if one of the given value is different than values
            of the given partner
        """
        keys_to_check = self._is_same_partner_value_keys_to_check(
            partner, vals
        )
        data = partner._convert_to_write(partner._cache)
        for key in keys_to_check:
            if data[key] != vals[key]:
                return False
        return True

    def _is_same_partner_value_keys_to_check(self, partner, vals):
        skip_keys = self._is_same_partner_value_skip_keys(partner)
        keys_to_check = []
        for key in vals.keys():
            if key in skip_keys or key not in partner:
                continue
            keys_to_check.append(key)
            # pylint: disable=pointless-statement
            partner[key]  # make sure key is cached
        return keys_to_check

    def _is_same_partner_value_skip_keys(self, partner):
        """Take control of keys to ignore for the match."""
        return ("backend_id", "partner_email")

    @api.model
    def _create_child_partner(self, parent, vals):
        vals = self._prepare_create_child_params(parent, vals)
        return self.env["res.partner"].create(vals)

    @api.model
    def _prepare_create_child_params(self, parent, vals):
        v = vals.copy()
        v["parent_id"] = parent.id
        if not v.get("type"):
            v["type"] = "other"
        v.pop("email")
        partner_fields = self.env["res.partner"]._fields
        # remove unknow partner fields
        for f in [i for i in v.keys()]:
            if f not in partner_fields:
                v.pop(f)
        return v

    def action_shopinvader_validate(self):
        wiz = self._get_shopinvader_validate_wizard()
        action = self.env.ref(
            "shopinvader.shopinvader_partner_validate_act_window"
        )
        action_data = action.read()[0]
        action_data["res_id"] = wiz.id
        return action_data

    def _get_shopinvader_validate_wizard(self, **kw):
        vals = dict(shopinvader_partner_ids=self.ids, **kw)
        return self.env["shopinvader.partner.validate"].create(vals)

    def action_edit_in_form(self):
        self.ensure_one()
        form_xid = self.env.context.get(
            "form_view_ref", "shopinvader.shopinvader_partner_view_form"
        )
        view = self.env.ref(form_xid)
        return {
            "name": _("Edit %s") % self.name,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "res_model": self._name,
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(self.env.context),
        }
