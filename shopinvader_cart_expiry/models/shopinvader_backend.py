# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.osv import expression


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    cart_expiry_delay = fields.Integer(
        string="Cart Expiry Delay (days)",
        help="Determine after how many days the old cart are expired/cleaned"
        "Let 0 (or less) to disable the feature.",
        default=0,
    )

    cart_expiry_policy = fields.Selection(
        selection=[("delete", "Delete"), ("cancel", "Cancel")],
        default="delete",
        help="Determine what to do with the cart when it expires.",
    )

    @api.model
    def _scheduler_manage_cart_expiry(self, domain=False):
        if not domain:
            domain = []
        domain = expression.AND([domain, [("cart_expiry_delay", ">", 0)]])
        for backend in self.search(domain):
            description = (
                _("Manage cart expired for backend %s") % backend.name
            )
            backend.with_delay(description=description).manage_cart_expiry()

    @job(default_channel="root.shopinvader")
    @api.multi
    def manage_cart_expiry(self):
        self.ensure_one()
        expiry_date = fields.Datetime.from_string(fields.Datetime.now())
        expiry_date -= timedelta(days=self.cart_expiry_delay)
        expiry_date = fields.Datetime.to_string(expiry_date)
        domain = [
            ("shopinvader_backend_id", "=", self.id),
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
            ("last_external_update_date", "<=", expiry_date),
        ]
        cart_expired = self.env["sale.order"].search(domain)
        if cart_expired:
            if self.cart_expiry_policy == "cancel":
                cart_expired.action_cancel()
            else:
                cart_expired.unlink()
