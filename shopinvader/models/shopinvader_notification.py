# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class ShopinvaderNotification(models.Model):
    _name = "shopinvader.notification"
    _description = "Shopinvader Notification"

    backend_id = fields.Many2one(
        "shopinvader.backend", "Backend", required=False
    )
    notification_type = fields.Selection(
        selection="_selection_notification_type",
        string="Notification Type",
        required=True,
    )
    model_id = fields.Many2one(
        "ir.model", "Model", required=True, ondelete="cascade"
    )
    template_id = fields.Many2one(
        "mail.template", "Mail Template", required=True
    )

    def _selection_notification_type(self):
        notifications = self._get_all_notification()
        return [(key, notifications[key]["name"]) for key in notifications]

    def _get_all_notification(self):
        return {
            "cart_confirmation": {
                "name": _("Cart Confirmation"),
                "model": "sale.order",
            },
            "cart_send_email": {
                "name": _("Cart ask by email"),
                "model": "sale.order",
            },
            "sale_send_email": {
                "name": _("Sale ask by email"),
                "model": "sale.order",
            },
            "sale_confirmation": {
                "name": _("Sale Confirmation"),
                "model": "sale.order",
            },
            "invoice_open": {
                "name": _("Invoice Validated"),
                "model": "account.invoice",
            },
            "invoice_send_email": {
                "name": _("Invoice send email"),
                "model": "account.invoice",
            },
            "new_customer_welcome": {
                "name": _("New customer Welcome"),
                "model": "res.partner",
            },
            "new_customer_welcome_not_validated": {
                "name": _("New customer Welcome not validated"),
                "model": "res.partner",
            },
            "customer_validated": {
                "name": _("New customer validated"),
                "model": "res.partner",
            },
            "customer_updated": {
                "name": _("Customer updated"),
                "model": "res.partner",
            },
            "address_created": {
                "name": _("Address created"),
                "model": "res.partner",
            },
            "address_created_not_validated": {
                "name": _("Address created not validated"),
                "model": "res.partner",
            },
            "address_validated": {
                "name": _("Address validated"),
                "model": "res.partner",
            },
            "address_updated": {
                "name": _("Address updated"),
                "model": "res.partner",
            },
        }

    @api.onchange("notification_type")
    def on_notification_type_change(self):
        self.ensure_one()
        notifications = self._get_all_notification()
        if self.notification_type:
            model = notifications[self.notification_type].get("model")
            if model:
                self.model_id = self.env["ir.model"].search(
                    [("model", "=", model)]
                )
                return {
                    "domain": {"model_id": [("id", "=", self.model_id.id)]}
                }
            else:
                return {"domain": {"model_id": []}}

    def send(self, record_id):
        self.ensure_one()
        return (
            self.sudo()
            .template_id.with_context(**self._get_template_context())
            .send_mail(record_id)
        )

    def _get_template_context(self):
        return {
            "notification_type": self.notification_type,
            "shopinvader_backend": self.backend_id,
            "website_name": self.backend_id.website_public_name,
        }
