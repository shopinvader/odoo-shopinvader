# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class PartnerEventListener(Component):
    _name = "shopinvader.autobind.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["res.partner"]

    def _send_bind_customers_email(self, backend, partners):
        template = backend.new_customer_autobind_mail_template_id
        if not template:
            return
        for partner in partners:
            template.send_mail(partner.id)

    def _bind_customers(self, record):
        """
        Get all backends that we want to bind to
        :param record:
        :return:
        """
        for backend in self.env["shopinvader.backend"].search(
            [("bind_new_customers", "=", True)]
        ):
            # Don't bind if record is already bound
            # sudo() because we could have in cache more than binding related to current company
            if record.sudo().shopinvader_bind_ids.filtered(
                lambda b: b.backend_id == backend
            ):
                continue
            wizard = (
                self.env["shopinvader.partner.binding"]
                .with_context(active_ids=record.ids, active_model=record._name)
                .create({"shopinvader_backend_id": backend.id})
            )
            wizard._onchange_shopinvader_backend_id()
            wizard.binding_lines.write({"bind": True})
            partners = wizard.binding_lines.mapped("partner_id")
            wizard.action_apply()
            self._send_bind_customers_email(backend, partners)

    def _get_write_fields(self):
        return ["email"]

    def _get_warning_message(self, record):
        return _(
            "The partner email is not defined! The account on websites "
            "is not created yet. "
            "Please fill in the email in order to do it."
        )

    def _check_partner(self, record, warn=True):
        if record.parent_id:
            return False
        if not record.email:
            if warn:
                self.env.user.notify_warning(
                    message=self._get_warning_message(record),
                    title="Website account not created.",
                )
            return False
        return True

    def _get_skip_if_condition(self, record, **kwargs):
        """
        Check if we have to skip the listener
        :param record: res.partner recordset
        :param kwargs: dict
        :return: bool
        """
        # When we're into the shopinvader_request, we don't have to
        # auto-bind because the guest service will create the
        # shopinvader.partner automatically
        if self.env.context.get("shopinvader_request"):
            return True
        return not bool(record.customer_rank)

    @skip_if(
        lambda self, record, **kwargs: self._get_skip_if_condition(record, **kwargs)
    )
    def on_record_create(self, record, fields=None):
        if not self._check_partner(record):
            return
        self._bind_customers(record)

    @skip_if(
        lambda self, record, **kwargs: self._get_skip_if_condition(record, **kwargs)
    )
    def on_record_write(self, record, fields=None):
        """
        If target fields are updated to trigger the website binding,
        bind customer to selected backends
        :param record:
        :param fields:
        :return:
        """
        # If target fields not in write(), don't go further
        if not fields or not any(
            field for field in fields if field in self._get_write_fields()
        ):
            return
        if not self._check_partner(record, warn=False):
            return
        self._bind_customers(record)
