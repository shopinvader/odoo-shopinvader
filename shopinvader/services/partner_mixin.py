# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super, consider-merging-classes-inherited

from odoo import _

from odoo.addons.component.core import AbstractComponent

# TODO: refactor out to a component event the handling of notifications


class PartnerServiceMixin(AbstractComponent):
    _name = "shopinvader.partner.service.mixin"

    @property
    def partner_validator(self):
        with self.shopinvader_backend.work_on(
            "res.partner", service_work=self.work
        ) as work:
            return work.component(usage="partner.validator")

    @property
    def access_info(self):
        with self.shopinvader_backend.work_on(
            "res.partner",
            partner=self.partner,
            partner_user=self.partner_user,
            invader_partner=self.invader_partner,
            invader_partner_user=self.invader_partner_user,
            service_work=self.work,
        ) as work:
            return work.component(usage="access.info")

    def _post_create(self, partner):
        self._notify_partner(partner, "create")
        self._notify_salesman(partner, "create")

    def _post_update(self, partner):
        self._notify_partner(partner, "update")
        self._notify_salesman(partner, "update")

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

    def _notify_salesman_values(self, partner, mode):
        # TODO: mode is not translated
        msg = _("{addr_type} {mode} '{name}' needs review").format(
            addr_type=partner.addr_type_display(), name=partner.name, mode=mode
        )
        return {
            "res_model_id": self.env.ref("base.model_res_partner").id,
            "res_id": self._notify_salesman_recipient(partner, mode).id,
            "user_id": self._get_salesman(partner).id,
            "activity_type_id": self.env.ref(
                "shopinvader.mail_activity_validate_customer"
            ).id,
            "summary": msg,
        }

    def _get_salesman(self, partner):
        """Retrieve salesman for the partner up to its hierarchy."""
        user = partner.user_id
        while not user and partner.parent_id:
            partner = partner.parent_id
            user = partner.user_id
        return user or self.env.user

    def _notify_partner(self, partner, mode):
        notif_type = self._notify_partner_type(partner, mode)
        recipient = self._notify_partner_recipient(partner, mode)
        if notif_type and recipient:
            self.shopinvader_backend._send_notification(notif_type, recipient)

    # HACK: these methods were supposed to be overriden in specific services
    # BUT the `customer` service has no `update` endpoint,
    # it relies on `addresses` endpoint for updates, hence
    # we are forced to discriminate on address type all in the same place.

    def _notify_partner_recipient(self, partner, mode):
        handler = getattr(
            self, "_notify_partner_recipient_" + partner.address_type, None
        )
        if handler:
            return handler(partner, mode)
        return partner

    def _notify_partner_recipient_address(self, partner, mode):
        # notify on the owner of the address
        # Safe default to given partner in case we are updating the profile
        # which is done w/ the addresses endpoint anyway.
        return partner.parent_id if partner.parent_id else partner

    def _notify_partner_type(self, partner, mode):
        handler = getattr(
            self, "_notify_partner_type_" + partner.address_type, None
        )
        if handler:
            return handler(partner, mode)
        return partner

    def _notify_partner_type_profile(self, partner, mode):
        notif = None
        if mode == "create":
            notif = "new_customer_welcome"
            if not self.partner_validator.is_partner_validated(partner):
                notif = "new_customer_welcome_not_validated"
        elif mode == "update":
            notif = "customer_updated"
        return notif

    def _notify_partner_type_address(self, partner, mode):
        notif = None
        if mode == "create":
            notif = "address_created"
            if not self.partner_validator.is_partner_validated(partner):
                notif = "address_created_not_validated"
        elif mode == "update":
            notif = "address_updated"
        return notif

    def _notify_salesman_recipient(self, partner, mode):
        handler = getattr(
            self, "_notify_salesman_recipient_" + partner.address_type, None
        )
        if handler:
            return handler(partner, mode)
        return partner

    def _notify_salesman_recipient_address(self, partner, mode):
        # notify on the owner of the address
        # Safe default to given partner in case we are updating the profile
        # which is done w/ the addresses endpoint anyway.
        return partner.parent_id if partner.parent_id else partner

    def _notify_salesman_needed(self, backend_policy, partner, mode):
        handler = getattr(
            self, "_notify_salesman_needed_" + partner.address_type, None
        )
        if handler:
            return handler(backend_policy, partner, mode)
        return partner

    def _notify_salesman_needed_address(self, backend_policy, partner, mode):
        return backend_policy in ("all", "address")

    def _notify_salesman_needed_profile(self, backend_policy, partner, mode):
        if backend_policy in ("all", "company_and_user"):
            return True
        elif backend_policy == "company" and partner.is_company:
            return True
        elif backend_policy == "user" and not partner.is_company:
            return True
        return False
