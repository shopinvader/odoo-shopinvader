#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from re import sub

from erpbrasil.base.fiscal.cnpj_cpf import validar

from odoo import _

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


try:
    from erpbrasil.base.fiscal import cnpj_cpf
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"
    _usage = "customer"

    def _prepare_params(self, params, mode="create"):
        if params.get("city_id"):
            params["city_id"] = (
                params.get("city_id")["id"]
                if type(params["city_id"]) == dict
                else params.get("city_id")
            )

        if params["state"]["id"] and not params["state"]["code"]:
            params["state_id"] = (
                params["state"]["id"]
                if type(params["state_id"]) == dict
                else params["state"]
            )
        if params["state"]["code"]:
            if params["country"]:
                state_id = self.env["res.country.state"].search(
                    [
                        ("code", "=", params["state"]["code"]),
                        ("country_id", "=", params["country"]["id"]),
                    ]
                )

        res = super(CustomerService, self)._prepare_params(params, mode)
        res["state_id"] = state_id.id
        return res

    @staticmethod
    def get_cnpj_cpf_type(raw_cnpj_cpf):
        cnpj_cpf = sub("[^0-9]", "", raw_cnpj_cpf)
        if len(cnpj_cpf) == 14:
            return "CNPJ"

        if len(cnpj_cpf) == 11:
            return "CPF"

    @restapi.method(
        [(["/search/cnpj_cpf/"], "GET")],
        input_param=restapi.CerberusValidator("_validator_search_cnpj_cpf"),
        output_param=restapi.CerberusValidator("_validator_return_search_cnpj_cpf"),
        cors="*",
    )
    def search_cnpj_cpf(self, **params):
        """Returns if either the cnpj or cpf is registered on the database."""
        cnpj_cpf_formatted = cnpj_cpf.formata(params.get("cnpj_cpf"))

        if not cnpj_cpf_formatted or not validar(cnpj_cpf_formatted):
            return {"registered": False, "message": _("Invalid input."), "type": ""}

        partner = self.env["res.partner"].search(
            [("cnpj_cpf", "ilike", cnpj_cpf_formatted)], limit=1
        )

        res = {"registered": partner.active}
        if partner.active:
            cnpj_cpf_type = self.get_cnpj_cpf_type(cnpj_cpf_formatted)
            res["message"] = _(f"This {cnpj_cpf_formatted} is already registered!")
            res["type"] = cnpj_cpf_type

        return res

    @staticmethod
    def _validator_search_cnpj_cpf():
        """It is necessary to enter the formatted Cpf or Cnpj"""
        return {"cnpj_cpf": {"type": "string", "required": True}}

    @staticmethod
    def _validator_return_search_cnpj_cpf():
        return {
            "registered": {"type": "boolean", "required": True},
            "message": {"type": "string", "required": False},
            "type": {"type": "string", "required": False},
        }
