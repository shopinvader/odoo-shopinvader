# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent
from odoo.osv import expression


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _default_domain_for_partner_records(
        self, partner_field="partner_id", with_backend=True
    ):
        domain = super()._default_domain_for_partner_records(
            partner_field=partner_field, with_backend=with_backend
        )
        # Change partner domain based on backend policy
        policy_field = self.shopinvader_backend.multi_user_records_policy
        # Remove partner leaf
        domain_no_partner = [x for x in domain if x[0] != partner_field]
        # Get a new partner domain
        partner_domain = self._partner_domain(partner_field, policy_field)
        return expression.AND([domain_no_partner, partner_domain])

    def _partner_domain(self, partner_field, policy_field):
        # Main users can always see everything down their hierarchy
        if self._is_admin_account():
            return [(partner_field, "child_of", self.partner.id)]

        if self._is_main_account():
            return [(partner_field, "child_of", self.partner.id)]

        related_partner = self.invader_partner[policy_field]
        main_account = self.invader_partner.main_partner_id
        partner_domains = [[(partner_field, "=", self.partner.id)]]
        if related_partner and not self.partner == related_partner:
            # See records from its related_partner (normally the parent)
            # but not other belonging to other users (like w/ child_of)
            partner_domains.append([(partner_field, "=", related_partner.id)])
            if main_account and main_account != related_partner:
                # See records from parent main account
                # NOTE: if main_account is the company,
                # they see records from the company as well.
                partner_domains.append([(partner_field, "=", main_account.id)])
        return expression.OR(partner_domains)

    def _is_admin_account(self):
        # Root account
        return not self.invader_partner.parent_id

    def _is_main_account(self):
        return (
            self.invader_partner.record_id
            == self.invader_partner.main_partner_id
        )
