# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.translate import _


class MembershipService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.membership.service"
    _usage = "membership"
    _expose_model = "membership.membership_line"
    _description = "Service providing a method to access membership lines"

    def _get_base_search_domain(self):
        """
        This method must provide a domain used to retrieve the requested
        membership lines.

        This domain MUST TAKE CARE of restricting the access to the membership
        lines visible for the current customer
        :return: Odoo domain
        """
        # The partner must be set and not be the anonymous one
        if not self._is_logged():
            return expression.FALSE_DOMAIN

        # here we only allow access to membership lines linked to the
        # current customer
        return expression.normalize_domain([("partner", "=", self.partner.id)])

    def search(self, **params):
        """
        Get every membership lines related to logged user
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def subscribe(self, _id):
        """
        Subscribe to a membership product with logged user
        :param _id: id of product.product
        :return: dict with invoice_id
        """
        if not self._is_logged():
            raise UserError(_("A user should be logged"))
        membership_product = self.env["product.product"].search(
            [("id", "=", _id), ("membership", "=", True)]
        )
        if not membership_product:
            raise UserError(_("No membership product found with id %s") % _id)
        wizard = self.env["membership.invoice"].create(
            {"product_id": _id, "member_price": membership_product.list_price}
        )
        invoices_views_dict = wizard.with_context(
            active_ids=self.partner.ids
        ).membership_invoice()
        return {"invoice_id": invoices_views_dict.get("domain")[0][2][0]}

    def _validator_subscribe(self):
        """
        Validator for the subscribe
        :return: dict
        """
        return {"membership_product_id": {"type": "integer"}}

    def _validator_return_subscribe(self):
        """
        Output validator for the subscribe
        :return: dict
        """
        return {"invoice_id": {"type": "integer"}}

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
        membership_line_schema = {
            "membership_line_id": {"type": "integer"},
            "date": {"type": "string", "nullable": True},
            "date_from": {"type": "string", "nullable": True},
            "date_to": {"type": "string", "nullable": True},
            "date_cancel": {"type": "string", "nullable": True},
            "membership_id": {
                "type": "dict",
                "nullable": True,
                "schema": {"name": {"type": "string"}},
            },
            "member_price": {"type": "float"},
            "state": {
                "type": "dict",
                "nullable": True,
                "schema": {
                    "value": {"type": "string"},
                    "label": {"type": "string"},
                },
            },
        }
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": membership_line_schema},
            },
        }
        return schema

    def _get_parser_membership_line(self):
        """
        Get the parser of membership.membership_line
        :return: list
        """
        to_parse = [
            "id:membership_line_id",
            "date",
            "date_from",
            "date_to",
            "date_cancel",
            ("membership_id:membership_id", ("name",)),
            "member_price",
        ]
        return to_parse

    def _get_selection_label(self, membership_line, field):
        """
        Get the translated label of the membership line selection field
        :param membership_line: membership.membership_line recordset
        :param field: str
        :return: str
        """
        if field not in membership_line._fields:
            return ""
        # convert_to_export(...) give the label of the selection (translated).
        return membership_line._fields.get(field).convert_to_export(
            membership_line[field], membership_line
        )

    def _to_json_membership_line(self, membership_line):
        membership_line.ensure_one()
        parser = self._get_parser_membership_line()
        values = membership_line.jsonify(parser)[0]
        values.update(
            {
                "state": {
                    "value": membership_line.state,
                    "label": self._get_selection_label(
                        membership_line, "state"
                    ),
                }
            }
        )
        return values

    def _to_json(self, membership_lines):
        res = []
        for membership_line in membership_lines:
            res.append(self._to_json_membership_line(membership_line))
        return res
