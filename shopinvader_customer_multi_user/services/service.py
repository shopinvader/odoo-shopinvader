# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    @property
    def invader_partner(self):
        partner = self.partner
        if partner:
            return partner._get_invader_partner(self.shopinvader_backend)
        return self.env["shopinvader.partner"].browse()

    def _default_domain_for_partner_records(
        self, partner_field="partner_id", with_backend=True
    ):
        # Change partner domain based on backend policy
        domain = [(partner_field, "child_of", self.partner.id)]
        if with_backend:
            domain.append(
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id)
            )
        policy_field = self.shopinvader_backend.multi_user_records_policy
        if policy_field == "record_id":
            return domain
        domain_no_partner = [x for x in domain if x[0] != partner_field]
        # keep a safe default
        partner = self.invader_partner.mapped(policy_field) or self.partner
        return domain_no_partner + [(partner_field, "child_of", partner.id)]
