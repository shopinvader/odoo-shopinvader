# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class PartnerEventListener(Component):
    _name = "shopinvader.autobind.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["res.partner"]

    def _get_write_fields(self):
        return ["email"]

    def _get_warning_message(self, record):
        return _(
            "The partner email is not defined! The account on websites "
            "is not created yet. "
            "Please fill in the email in order to do it."
        )

    def _check_partner(self, record, warn=True):
        if not record.email:
            if warn:
                self.env.user.notify_warning(
                    message=self._get_warning_message(record),
                    title="Website account not created.",
                )
            return False
        return True

    @skip_if(lambda self, record, **kwargs: not record.customer)
    def on_record_create(self, record, fields=None):
        if not self._check_partner(record):
            return
        for backend in self.env["shopinvader.backend"].search(
            [("bind_new_customers", "=", True)]
        ):
            wizard = (
                self.env["shopinvader.partner.binding"]
                .with_context(
                    active_ids=record.ids, active_model="res.partner"
                )
                .create({"shopinvader_backend_id": backend.id})
            )
            wizard._onchange_shopinvader_backend_id()
            wizard.binding_lines.write({"bind": True})
            wizard.action_apply()

    @skip_if(lambda self, record, **kwargs: not record.customer)
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
        for backend in self.env["shopinvader.backend"].search(
            [("bind_new_customers", "=", True)]
        ):
            # Don't bind if record is already bound
            if record.shopinvader_bind_ids.filtered(
                lambda b: b.backend_id == backend
            ):
                continue
            wizard = (
                self.env["shopinvader.partner.binding"]
                .with_context(
                    active_ids=record.ids, active_model="res.partner"
                )
                .create({"shopinvader_backend_id": backend.id})
            )
            wizard._onchange_shopinvader_backend_id()
            wizard.binding_lines.write({"bind": True})
            wizard.action_apply()
