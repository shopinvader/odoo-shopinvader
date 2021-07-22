# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    # FIXME: this could be avoided if we had `update` endpoint on `customer`.
    # See https://github.com/shopinvader/odoo-shopinvader/issues/530
    def _store_cache_needed(self, partner):
        needed = super()._store_cache_needed(partner)
        backend = self.shopinvader_backend
        shop_partner = partner.get_shop_partner(backend)
        # if the shop partner is the same as the profile one
        # then we want to cache it.
        return needed or shop_partner == partner

    def _default_domain_for_partner_records(
        self, partner_field="partner_id", operator="=", with_backend=True, **kw
    ):
        if not self.shopinvader_backend.customer_multi_user:
            return super()._default_domain_for_partner_records(
                partner_field=partner_field,
                operator=operator,
                with_backend=with_backend,
                **kw
            )
        # Complete override of domain generation as there's complex logic
        # which is delegated completely to `_make_address_domain`
        domains = [
            [("type", "in", ("delivery", "invoice", "contact", "other"))],
            self.invader_partner_user._make_address_domain(),
        ]
        return expression.AND(domains)

    def _get_allowed_share_policy_values(self):
        field = self.env["res.partner"]._fields["invader_address_share_policy"]
        return [x[0] for x in field.selection]

    def _validator_create(self):
        res = super()._validator_create()
        res.update(
            {
                "share_policy": {
                    "type": "string",
                    "required": False,
                    "empty": False,
                    "allowed": self._get_allowed_share_policy_values(),
                }
            }
        )
        return res

    def _json_parser(self):
        res = super()._json_parser()
        res.append("invader_address_share_policy:share_policy")
        return res

    def _prepare_params(self, params, mode="create"):
        res = super()._prepare_params(params, mode=mode)
        if res.get("share_policy"):
            res["invader_address_share_policy"] = res.pop("share_policy")
        return res
