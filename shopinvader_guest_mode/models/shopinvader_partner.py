# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from functools import wraps

import psycopg2
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def wrap_integrity_error(method):
    @wraps(method)
    def f(*args, **kwargs):
        try:
            r = method(*args, **kwargs)
        except psycopg2.IntegrityError as inst:
            constrains = {
                "unique_shopinvader_partner_email": _(
                    "Only one active binging with the same email is "
                    "allowed by backend."
                )
            }
            for key in constrains:
                if key in inst[0]:
                    raise ValidationError(constrains[key])
            raise
        return r

    return f


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    is_guest = fields.Boolean(
        help="If true, the partner will be automatically deactivated once the "
        "expiry date will be passed",
        index=True,
    )

    expiry_dt = fields.Datetime(
        "Expiry date and time",
        compute="_compute_expiry_dt",
        help="Date on which the account will be automatically deactivated if"
        "the customer has not created an account.",
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True, index=True)

    _sql_constraints = [
        # Replaced by an unique index on active binding
        ("record_uniq", "CHECK(1=1)", ""),
        # Replaced by an unique index on active binding
        ("email_uniq", "CHECK(1=1)", ""),
    ]

    @api.model_cr
    def init(self):
        """
        Create unique index only for active records
        """
        res = super(ShopinvaderPartner, self).init()
        self._cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s",
            ("unique_shopinvader_partner_email",),
        )
        if not self._cr.fetchone():
            self._cr.execute(
                """
            CREATE UNIQUE INDEX unique_shopinvader_partner_email
            ON shopinvader_partner (backend_id, partner_email)
            WHERE active;
            """
            )
        return res

    @api.multi
    @api.constrains("is_guest")
    def _check_is_guest_mode_allowed(self):
        recs = self.filtered(
            lambda r: r.is_guest and not r.backend_id.is_guest_mode_allowed
        )
        if recs:
            raise ValidationError(
                _(
                    "You can't create guest binding if the guest mode is not"
                    "allowed on the backend."
                )
            )

    @api.multi
    @api.depends("backend_id.guest_account_expiry_delay", "is_guest")
    def _compute_expiry_dt(self):
        for record in self:
            if not record.is_guest:
                record.expiry_dt = False
                continue
            create_date = fields.Datetime.from_string(record.create_date)
            delay = record.backend_id.guest_account_expiry_delay
            expiry_dt = create_date + timedelta(days=delay)
            record.expiry_dt = fields.Datetime.to_string(expiry_dt)

    @api.model
    def _deactivate_expired(self):
        expired = self.search(
            [
                ("is_guest", "=", True),
                ("expiry_dt", "<", fields.Datetime.now()),
            ]
        )
        expired.write({"active": False})

    @wrap_integrity_error
    @api.model
    def create(self, vals):
        return super(ShopinvaderPartner, self).create(vals)

    @wrap_integrity_error
    @api.multi
    def write(self, vals):
        return super(ShopinvaderPartner, self).write(vals)
