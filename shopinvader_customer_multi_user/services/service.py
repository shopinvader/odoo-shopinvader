# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _default_domain_for_partner_records(
        self, partner_field="partner_id", operator="=", with_backend=True, **kw
    ):
        domain = super()._default_domain_for_partner_records(
            partner_field=partner_field,
            operator=operator,
            with_backend=with_backend,
            **kw
        )
        # Remove partner leaf
        domain_no_partner = [x for x in domain if x[0] != partner_field]
        # Get a new partner domain
        partner_domain = self.invader_partner_user._make_partner_domain(
            partner_field, operator=operator, **kw
        )
        return expression.AND([domain_no_partner, partner_domain])
