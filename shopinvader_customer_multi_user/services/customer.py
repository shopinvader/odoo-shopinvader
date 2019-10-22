# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _prepare_params(self, params):
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
                        "type": self.env[
                            "res.partner"
                        ].invader_client_user_type(),
                    }
                )
        return vals

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update({"company_token": {"type": "string", "required": False}})
        return schema

    def _to_customer_info(self, partner):
        info = super()._to_customer_info(partner)
        info["company_token"] = partner.invader_user_token
        info["is_company"] = self.partner_user.is_company
        return info
