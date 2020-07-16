# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv import expression


class MembershipService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.membership.product.service"
    _usage = "membership_product"
    _expose_model = "product.product"
    _description = "Service providing a method to access membership products"

    def _get_base_search_domain(self):
        """
        This method must provide a domain used to retrieve the requested
        membership products.

        :return: Odoo domain
        """

        # here we only allow access to membership products
        return expression.normalize_domain([("membership", "=", True)])

    def search(self, **params):
        """
        Get every membership products
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def _validator_search(self):
        """
        Validator for the search
        :return: dict
        """
        schema = {
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
        }
        return schema

    def _validator_return_search(self):
        """
        Output validator for the search
        :return: dict
        """
        membership_product_schema = {
            "name": {"type": "string", "nullable": True},
            "default_code": {"type": "string", "nullable": True},
            "description_sale": {"type": "string", "nullable": True},
            "list_price": {"type": "float"},
        }
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": membership_product_schema,
                },
            },
        }
        return schema

    def _get_parser_membership_product(self):
        """
        Get the parser of membership products
        :return: list
        """
        to_parse = ["name", "default_code", "description_sale", "list_price"]
        return to_parse

    def _to_json_membership_product(self, membership_product):
        membership_product.ensure_one()
        parser = self._get_parser_membership_product()
        values = membership_product.jsonify(parser)[0]
        return values

    def _to_json(self, membership_products):
        res = []
        for membership_product in membership_products:
            res.append(self._to_json_membership_product(membership_product))
        return res
