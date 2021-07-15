# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class PartnerServiceMixin(AbstractComponent):
    _inherit = "shopinvader.partner.service.mixin"

    @property
    def partner_validator(self):
        with self.shopinvader_backend.work_on(
            "res.partner", service_work=self.work
        ) as work:
            return work.component(usage="partner.validator")

    def _notify_partner_type_profile(self, partner, mode):
        notif = super()._notify_partner_type_profile(partner, mode)
        if mode == "create" and not self.partner_validator.is_partner_validated(
            partner
        ):
            notif = "new_customer_welcome_not_validated"
        return notif

    def _notify_partner_type_address(self, partner, mode):
        notif = super()._notify_partner_type_address(partner, mode)
        if mode == "create" and not self.partner_validator.is_partner_validated(
            partner
        ):
            notif = "address_created_not_validated"
        return notif

    def _notify_salesman_needed(self, backend_policy, partner, mode):
        if not self.partner_validator.is_partner_validated(partner):
            # always notify if validation needed
            return True
        return super()._notify_salesman_needed(backend_policy, partner, mode)
