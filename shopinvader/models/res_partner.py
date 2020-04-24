# -*- coding: utf-8 -*-
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
        string="Address Type",
        compute="_compute_address_type",
        store=True,
    )
    # In europe we use more the opt_in
    opt_in = fields.Boolean(
        compute="_compute_opt_in", inverse="_inverse_opt_in"
    )

    @api.multi
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

    @api.depends("opt_out")
    def _compute_opt_in(self):
        for record in self:
            record.opt_in = not record.opt_out

    def _inverse_opt_in(self):
        for record in self:
            record.opt_out = not record.opt_in

    @api.depends("parent_id")
    def _compute_address_type(self):
        for partner in self:
            if partner.parent_id:
                partner.address_type = "address"
            else:
                partner.address_type = "profile"

    @api.multi
    def write(self, vals):
        super(ResPartner, self).write(vals)
        if "country_id" in vals:
            carts = self.env["sale.order"].search(
                [
                    ("typology", "=", "cart"),
                    ("partner_shipping_id", "in", self.ids),
                ]
            )
            for cart in carts:
                # Trigger a write on cart to recompute the
                # fiscal position if needed
                cart.write_with_onchange(
                    {"partner_shipping_id": cart.partner_shipping_id.id}
                )
        return True
