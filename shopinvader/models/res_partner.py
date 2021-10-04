# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import str2bool

from .shopinvader_partner import STATE_ACTIVE, STATE_PENDING


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.partner", "record_id", string="Shopinvader Binding"
    )
    # TODO: this field should be renamed to `shopinvader_type`
    # and should be valued like:
    # - profile = main account
    # - address = just an address
    #   that belongs to a partner with shopinvader_type == 'profile'
    # - user or childuser = has a shop user and is child of a profile
    # This way we can get rid of many computations like
    # `parent_has_shopinvader_user` or `has_shopinvader_user`
    address_type = fields.Selection(
        selection=[("profile", "Profile"), ("address", "Address")],
        string="Shopinvader Address Type",
        compute="_compute_address_type",
        store=True,
    )
    # In europe we use more the opt_in
    opt_in = fields.Boolean(
        compute="_compute_opt_in", inverse="_inverse_opt_in"
    )
    is_shopinvader_active = fields.Boolean(
        string="Shop enabled",
        help="This address is enabled to be used for Shopinvader.",
    )
    parent_has_shopinvader_user = fields.Boolean(
        help="This partner belongs to Shopinvader user.",
        compute="_compute_parent_has_shopinvader_user",
        compute_sudo=True,
        store=True,
    )
    has_shopinvader_user = fields.Boolean(
        help="This partner has at least a Shopinvader user.",
        compute="_compute_has_shopinvader_user",
        compute_sudo=True,
    )
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

    @api.model
    def _is_partner_duplicate_prevented(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return str2bool(get_param("shopinvader.no_partner_duplicate"))

    @api.depends("is_blacklisted")
    def _compute_opt_in(self):
        for record in self:
            record.opt_in = not record.is_blacklisted

    def _inverse_opt_in(self):
        blacklist_model = self.env["mail.blacklist"]
        for record in self:
            if record.opt_in:
                blacklist_model._remove(record.email)
            else:
                blacklist_model._add(record.email)

    @api.depends("parent_id.shopinvader_bind_ids")
    def _compute_parent_has_shopinvader_user(self):
        for record in self:
            record.parent_has_shopinvader_user = bool(
                record.parent_id.shopinvader_bind_ids
            )

    @api.depends("shopinvader_bind_ids.state")
    def _compute_has_shopinvader_user(self):
        for record in self:
            record.has_shopinvader_user = bool(record.shopinvader_bind_ids)
            record.has_shopinvader_user_active = any(
                record.shopinvader_bind_ids.filtered(
                    lambda x: x.state == STATE_ACTIVE
                )
            )
            record.has_shopinvader_user_to_validate = any(
                record.shopinvader_bind_ids.filtered(
                    lambda x: x.state == STATE_PENDING
                )
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
            record.has_shopinvader_address_to_validate = bool(
                by_parent.get(record.id)
            )

    def _compute_display_flags(self):
        for record in self:
            record.display_validate_address = (
                record._display_validate_address()
            )

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

    @api.depends("parent_id")
    def _compute_address_type(self):
        for partner in self:
            if partner.parent_id:
                partner.address_type = "address"
            else:
                partner.address_type = "profile"

    @api.constrains("email", "has_shopinvader_user_active")
    def _check_unique_email(self):
        if not self._is_partner_duplicate_prevented():
            return True
        self.env["res.partner"].flush(["email", "has_shopinvader_user_active"])
        self.env.cr.execute(
            """
            SELECT
                email
            FROM (
                SELECT
                    id,
                    email,
                    ROW_NUMBER() OVER (PARTITION BY email) AS Row
                FROM
                    res_partner
                WHERE email is not null
                    and active = True
                    and has_shopinvader_user_active = True
                ) dups
            WHERE dups.Row > 1;
        """
        )
        duplicate_emails = {r[0] for r in self.env.cr.fetchall()}
        invalid_emails = [
            e for e in self.mapped("email") if e in duplicate_emails
        ]
        if invalid_emails:
            raise ValidationError(
                _(
                    "Email must be unique: The following "
                    "mails are not unique: %s"
                )
                % ", ".join(invalid_emails)
            )

    def write(self, vals):
        super(ResPartner, self).write(vals)
        if "country_id" in vals:
            carts = (
                self.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("typology", "=", "cart"),
                        ("partner_shipping_id", "in", self.ids),
                    ]
                )
            )
            for cart in carts:
                # Trigger a write on cart to recompute the
                # fiscal position if needed
                cart.sudo().write_with_onchange(
                    {"partner_shipping_id": cart.partner_shipping_id.id}
                )
        return True

    def addr_type_display(self):
        return self._fields["address_type"].convert_to_export(
            self.address_type, self
        )

    def action_shopinvader_validate_customer(self):
        return self.shopinvader_bind_ids.action_shopinvader_validate()

    def action_shopinvader_validate_address(self):
        wiz = self._get_shopinvader_validate_address_wizard()
        action = self.env.ref(
            "shopinvader.shopinvader_address_validate_act_window"
        )
        action_data = action.read()[0]
        action_data["res_id"] = wiz.id
        return action_data

    def _get_shopinvader_validate_address_wizard(self, **kw):
        ids = self.ids
        if self.env.context.get("validate_all"):
            ids = self.child_ids.filtered_domain(
                [
                    ("has_shopinvader_user", "=", False),
                    ("address_type", "=", "address"),
                    ("is_shopinvader_active", "=", False),
                ]
            ).ids
        vals = dict(partner_ids=ids, **kw)
        return self.env["shopinvader.address.validate"].create(vals)

    def get_shop_partner(self, backend):
        """Retrieve current partner customer account.

        By default is the same user's partner.
        Hook here to provide your own behavior.

        This partner is used to provide main account information client side
        and to assign the partner to the sale order / cart.

        :return: res.partner record.
        """
        return self

    def _get_invader_partner(self, backend):
        """Get bound partner matching backend."""
        domain = [("backend_id", "=", backend.id)]
        return self.shopinvader_bind_ids.filtered_domain(domain)
