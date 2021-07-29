# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _prepare_params(self, params, mode="create"):
        vals = super()._prepare_params(params, mode=mode)
        company_token = vals.pop("company_token", None)
        if company_token and self.shopinvader_backend.customer_multi_user:
            # retrieve the company
            company = self.env["res.partner"].find_by_invader_user_token(company_token)
            if company:
                # set parent and specific type
                vals.pop("is_company", None)
                vals.update(
                    {
                        "parent_id": company.id,
                        "type": vals.get(
                            "type",
                            self._default_simple_user_partner_type(company),
                        ),
                    }
                )
        return vals

    def _default_simple_user_partner_type(self, company):
        return "contact"

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update({"company_token": {"type": "string", "required": False}})
        # TODO: address fields should not be required
        # when you register a new user for a company
        # hence when the company token is there address fields should be
        # non required.
        return schema

    def _to_customer_info(self, partner):
        info = super()._to_customer_info(partner)
        if not self.shopinvader_backend.customer_multi_user:
            return info
        if partner.is_company:
            info["company_token"] = partner.invader_user_token
        invader_partner = self.invader_partner_user
        info["is_simple_user"] = invader_partner.is_invader_user
        info["main_account"] = self._get_main_account_info(invader_partner)
        return info

    def _get_main_account_info(self, invader_partner):
        if (
            not invader_partner.main_partner_id
            or invader_partner.record_id == invader_partner.main_partner_id
        ):
            # the partner is already the main one
            return None
        return invader_partner.main_partner_id.jsonify(
            self._json_parser_main_account(), one=True
        )

    def _json_parser_main_account(self):
        return [("id", lambda rec, fname: rec.id), "name", "ref"]
