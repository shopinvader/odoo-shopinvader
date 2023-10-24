# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.translate import _

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


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
        if not self._is_logged_in():
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

    @restapi.method(
        [(["/<int:_id>/subscribe"], "GET")],
        input_param=restapi.CerberusValidator({}),
        output_param=restapi.CerberusValidator("_validator_return_subscribe"),
    )
    def get_subscribe(self, _id):
        """
        DEPRECATED: you should use `subscribe` with a POST.
        Subscribe to a membership product with logged user
        :param _id: id of product.product
        :return: dict with invoice_id
        """
        _logger.warning("DEPRECATED: You should use `subscribe` with a POST")
        return self.post_subscribe(**{"membership_product_id": _id})

    @restapi.method(
        [(["/subscribe"], "POST")],
        input_param=restapi.CerberusValidator("_validator_subscribe"),
        output_param=restapi.CerberusValidator("_validator_return_subscribe"),
    )
    def post_subscribe(self, **params):
        """
        Subscribe to a membership product with logged user
        :return: dict with invoice_id
        """
        product_id = params.get("membership_product_id")
        if not self._is_logged_in():
            raise UserError(_("A user should be logged"))
        membership_product = self.env["product.product"].search(
            [("id", "=", product_id), ("membership", "=", True)], limit=1
        )
        if not membership_product:
            raise UserError(_("No membership product found with id %s") % product_id)
        wizard = self.env["membership.invoice"].create(
            {"product_id": product_id, "member_price": membership_product.list_price}
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
        return {"membership_product_id": {"type": "integer", "required": True}}

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
                "schema": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                },
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
            ("membership_id:membership_id", ("id", "name")),
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
                    "label": self._get_selection_label(membership_line, "state"),
                }
            }
        )
        return values

    def _to_json(self, membership_lines):
        res = []
        for membership_line in membership_lines:
            res.append(self._to_json_membership_line(membership_line))
        return res
