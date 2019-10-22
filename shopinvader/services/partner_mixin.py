# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super, consider-merging-classes-inherited

from odoo import _
from odoo.addons.component.core import AbstractComponent

# TODO: refactor out to a component event the handling of notifications


class PartnerServiceMixin(AbstractComponent):
    _name = "shopinvader.partner.service.mixin"

    def _post_create(self, partner):
        self._notify_partner(partner, "create")
        self._notify_salesman(partner, "create")

    def _post_update(self, partner):
        self._notify_partner(partner, "update")
        self._notify_salesman(partner, "update")

    @property
    def partner_validator(self):
        with self.shopinvader_backend.work_on("res.partner") as work:
            return work.component(usage="partner.validator")

    def _notify_salesman(self, partner, mode):
        needed = False
        if not self.partner_validator.is_partner_validated(partner):
            # always notify if validation needed
            needed = True
        backend_policy = self.shopinvader_backend["salesman_notify_" + mode]
        needed = self._notify_salesman_needed(backend_policy, partner, mode)
        if needed:
            self.env["mail.activity"].sudo().create(
                self._notify_salesman_values(partner, mode)
            )

    def _notify_salesman_needed(self, backend_policy, partner, mode):
        raise NotImplementedError()

    def _notify_salesman_values(self, partner, mode):
        return {
            "res_model_id": self.env.ref("base.model_res_partner").id,
            "res_id": partner.id,
            "user_id": self._get_salesman(partner).id,
            "activity_type_id": self.env.ref(
                "shopinvader.mail_activity_validate_customer"
            ).id,
            "summary": _("Partner needs review"),
        }

    def _get_salesman(self, partner):
        """Retrieve salesman for the partner up to its hierarchy."""
        user = partner.user_id
        while not user and partner.parent_id:
            partner = partner.parent_id
            user = partner.user_id
        return user or self.env.user

    def _notify_partner(self, partner, mode):
        notif_type = self._get_notification_type(partner, mode)
        if notif_type:
            self.shopinvader_backend._send_notification(
                notif_type, self._get_notification_recipient(partner, mode)
            )

    def _get_notification_recipient(self, partner, mode):
        return partner

    def _get_notification_type(self, partner, mode):
        raise NotImplementedError()
