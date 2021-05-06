# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import _
from odoo.exceptions import MissingError, UserError
from odoo.osv import expression

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import AbstractComponent

from .. import shopinvader_response, utils

_logger = logging.getLogger(__name__)


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.shopinvader.service"
    _collection = "shopinvader.backend"
    _expose_model = None

    def _load_partner_work_context(self, invader_partner, force=False):
        utils.load_partner_work_ctx(self, invader_partner, force=force)

    def _reset_partner_work_context(self):
        # Basically like logging out a user
        utils.reset_partner_work_ctx(self)

    @property
    def partner(self):
        # partner that matches the real profile on client side
        # or its main contact which in any case is used for all
        # account information.
        return self.work.partner

    @property
    def invader_partner(self):
        return self.work.invader_partner

    @property
    def partner_user(self):
        # partner that matches the real user on client side.
        # The standard `self.partner` will match `partner_user`
        # only when the main customer account is logged in.
        # In this way we can support multiple actors for the same profile.
        # TODO: check if there are place wher it's better to use
        # `partner_user` instead of `partner`.
        return getattr(self.work, "partner_user", self.partner)

    @property
    def invader_partner_user(self):
        return self.work.invader_partner_user

    @property
    def shopinvader_session(self):
        return self.work.shopinvader_session

    @property
    def shopinvader_backend(self):
        return self.work.shopinvader_backend

    @property
    def client_header(self):
        return self.work.client_header

    _scope_to_domain_operators = {
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
        "ne": "!=",
        "like": "like",
        "ilike": "ilike",
    }

    def _scope_to_domain(self, scope):
        # Convert the frontend scope syntax to the odoo domain
        try:
            domain = []
            for key, value in scope.items():
                if "." in key:
                    key, op = key.split(".")
                    op = self._scope_to_domain_operators[op]
                else:
                    op = "="
                domain.append((key, op, value))
            return domain
        except Exception as e:
            raise UserError(
                _("Invalid scope %s, error: %s") % (str(scope), str(e))
            )

    # Validator
    def _default_validator_search(self):
        """
        Get a default validator for search service.
        This search include every parameters used for pagination, scope and domain.
        This directly used a _validator_search in case of an existing service
        doesn't allow all of these parameters (backward compatibility).
        :return: dict
        """
        return {
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "domain": {"type": "list", "nullable": True},
            "scope": {"type": "dict", "nullable": True},
            "order": {"type": "string", "nullable": True},
        }

    def _paginate_search(
        self, default_page=1, default_per_page=5, order=None, **params
    ):
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
            domain,
            limit=per_page,
            offset=per_page * (page - 1),
            order=self._get_search_order(order, **params),
        )
        return {"size": total_count, "data": self._to_json(records, **params)}

    def _get_search_order(self, order, **params):
        """Customize search results order.

        By default, simply pass the *internal odoo field* you want to sort on
        (eg: 'date_order desc').

        Override to define special sorting policies.
        """
        return order

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

    def _default_domain_for_partner_records(
        self, partner_field="partner_id", operator="=", with_backend=True, **kw
    ):
        """Domain to filter records bound to current partner and backend.
        """
        domain = [(partner_field, operator, self.partner.id)]
        if with_backend:
            domain.append(
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id)
            )
        return domain

    def _get_selection_label(self, record, field):
        """
        Get the translated label of the record selection field
        :param record: recordset
        :param field: str
        :return: str
        """
        if field not in record._fields:
            return ""
        # convert_to_export(...) give the label of the selection (translated).
        return record._fields.get(field).convert_to_export(
            record[field], record
        )

    def _get_openapi_default_parameters(self):
        defaults = super(
            BaseShopinvaderService, self
        )._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "API-KEY",
                "in": "header",
                "description": "Auth API key",
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

    def _is_logged_in(self):
        """
        Check if the current partner is a real partner (not the anonymous one
        and not empty)
        :return: bool
        """
        logged = False
        if (
            self.partner
            and self.partner != self.shopinvader_backend.anonymous_partner_id
        ):
            logged = True
        return logged

    def _is_logged(self):
        _logger.warning("DEPRECATED: You should use `self._is_logged_in()`")
        return self._is_logged_in()

    @property
    def shopinvader_response(self):
        """
        An instance of
        ``odoo.addons.shopinvader.shopinvader_response.ShopinvaderResponse``.
        """
        return shopinvader_response.get()

    def dispatch(self, method_name, *args, params=None):
        res = super().dispatch(method_name, *args, params=params)
        store_cache = self.shopinvader_response.store_cache
        if store_cache:
            values = res.get("store_cache", {})
            values.update(store_cache)
            res["store_cache"] = values
        session = self.shopinvader_response.session
        if session:
            values = res.get("set_session", {})
            values.update(session)
            res["set_session"] = values
        return res
