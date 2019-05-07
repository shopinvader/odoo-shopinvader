# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _
from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import MissingError, UserError
from odoo.osv import expression


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.shopinvader.service"
    _collection = "shopinvader.backend"
    _expose_model = None

    @property
    def partner(self):
        return self.work.partner

    @property
    def shopinvader_session(self):
        return self.work.shopinvader_session

    @property
    def shopinvader_backend(self):
        return self.work.shopinvader_backend

    @property
    def client_header(self):
        return self.work.client_header

    def _scope_to_domain(self, scope):
        # Convert the liquid scope syntax to the odoo domain
        try:
            OPERATORS = {
                "gt": ">",
                "gte": ">=",
                "lt": "<",
                "lte": "<=",
                "ne": "!=",
            }
            domain = []
            for key, value in scope.items():
                if "." in key:
                    key, op = key.split(".")
                    op = OPERATORS[op]
                else:
                    op = "="
                domain.append((key, op, value))
            return domain
        except Exception as e:
            raise UserError(_("Invalid scope %s, error : %s"), scope, e)

    def _paginate_search(self, default_page=1, default_per_page=5, **params):
        """
        Build a domain and search on it.
        As we use expression (from Odoo), manuals domains get from "scope" and
        "domain" keys are normalized to avoid issues.
        :param default_page: int
        :param default_per_page: int
        :param params: dict
        :return: dict
        """
        domain = self._get_base_search_domain()
        if params.get("scope"):
            scope_domain = self._scope_to_domain(params.get("scope"))
            scope_domain = expression.normalize_domain(scope_domain)
            domain = expression.AND([domain, scope_domain])
        if params.get("domain"):
            custom_domain = expression.normalize_domain(params.get("domain"))
            domain = expression.AND([domain, custom_domain])
        model_obj = self.env[self._expose_model]
        total_count = model_obj.search_count(domain)
        page = params.get("page", default_page)
        per_page = params.get("per_page", default_per_page)
        records = model_obj.search(
            domain, limit=per_page, offset=per_page * (page - 1)
        )
        return {"size": total_count, "data": self._to_json(records)}

    def _get(self, _id):
        domain = expression.normalize_domain(self._get_base_search_domain())
        domain = expression.AND([domain, [("id", "=", _id)]])
        record = self.env[self._expose_model].search(domain)
        if not record:
            raise MissingError(
                _("The record %s %s does not exist")
                % (self._expose_model, _id)
            )
        else:
            return record

    def _get_base_search_domain(self):
        return []

    def _get_openapi_default_parameters(self):
        defaults = super(
            BaseShopinvaderService, self
        )._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "API-KEY",
                "in": "header",
                "description": "Ath API key",
                "required": True,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        defaults.append(
            {
                "name": "PARTNER-EMAIL",
                "in": "header",
                "description": "Logged partner email",
                "required": False,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        return defaults
