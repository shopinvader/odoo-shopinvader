# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.partner", "record_id", string="Shopinvader Binding"
    )
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
    shopinvader_enabled = fields.Boolean(
        string="Shop enabled",
        default=True,
        help="Enable user account on the frontend. "
        "If this is disabled the user cannot log in on all the websites. "
        "This behavior must be enabled on the backend "
        "via 'Validate customers' flag.",
    )

    @api.constrains("email")
    def _check_unique_email(self):
        config = self.env["shopinvader.config.settings"]
        if config.is_partner_duplication_allowed():
            return True
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
                WHERE email is not null and active = True
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

    @api.depends("parent_id")
    def _compute_address_type(self):
        for partner in self:
            if partner.parent_id:
                partner.address_type = "address"
            else:
                partner.address_type = "profile"

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

    def action_enable_for_shop(self):
        self.write({"shopinvader_enabled": True})
        # TODO: maybe better to hook to an event?
        for partner in self:
            if partner.address_type == "profile":
                notif_type = "customer_validated"
                backends = partner.mapped("shopinvader_bind_ids.backend_id")
                recipient = partner
            elif partner.address_type == "address":
                notif_type = "address_validated"
                backends = partner.mapped(
                    "parent_id.shopinvader_bind_ids.backend_id"
                )
                recipient = partner.parent_id
            recipient._shopinvader_notify(backends, notif_type)
            name = partner.name or partner.contact_address.replace("\n", " | ")
            msg_body = _("Shop {addr_type} '{name}' validated").format(
                addr_type=partner.addr_type_display().lower(), name=name
            )
            recipient.message_post(body=msg_body)

    def _shopinvader_notify(self, backends, notif_type):
        self.ensure_one()
        for backend in backends:
            backend._send_notification(notif_type, self)

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
