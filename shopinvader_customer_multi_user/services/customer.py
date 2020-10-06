# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _prepare_params(self, params, mode="create"):
        vals = super()._prepare_params(params)
        company_token = vals.pop("company_token", None)
        if company_token and self.shopinvader_backend.customer_multi_user:
            # retrieve the company
            company = self.env["res.partner"].find_by_invader_user_token(
                company_token
            )
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
        info["company_token"] = partner.invader_user_token
        info["main_account"] = self._get_main_account_info(partner)
        return info

    def _get_main_account_info(self, partner):
        invader_partner = partner._get_invader_partner(
            self.shopinvader_backend
        )
        return invader_partner.main_partner_id.jsonify(
            self._json_parser_main_account(), one=True
        )

    def _json_parser_main_account(self):
        return [("id", lambda rec, fname: rec.record_id.id), "name", "ref"]
