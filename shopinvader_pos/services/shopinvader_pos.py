# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.osv import expression
from odoo.tools import float_round

from odoo.addons.component.core import Component


class ShopinvaderPoS(Component):
    _inherit = ["base.shopinvader.service"]
    _name = "shopinvader.pos.service"
    _usage = "point_of_sale"
    _expose_model = "pos.order"

    def search(self, **params):
        """

        :param params: dict/json
        :return: get on updated recordset
        """
        values = self._search(params)
        return values

    def get(self, _id=False):
        """

        :param _id: int (optional)
        :return: dict/json
        """
        pos_order = super()._get(_id)
        jsonified_record = self._to_json(pos_order)[0]
        values = {"data": jsonified_record}
        return values

    def _get_base_search_domain(self):
        """
        Inherit to have a common domain specific to PoS
        :return: list of tuple (domain)
        """
        domain = [("state", "in", ("paid", "done", "invoiced"))]
        partner = self._get_current_partner()
        # If no logged partner, we don't have to display anything.
        partner_domain = expression.FALSE_DOMAIN
        if partner:
            partner_domain = [("partner_id", "child_of", partner.id)]
        domain = expression.AND([domain, partner_domain])
        return domain

    def _get_current_partner(self):
        """
        Get current logged partner.
        The partner is empty if the current logged user is the anonymous one
        :return: res.partner recordset
        """
        if self._is_logged_in():
            return self.partner
        return self.env["res.partner"].browse()

    def _search(self, params):
        """
        Build the search result in json/dict.
        The front side can fill a "value" parameter to do a search on
        the pos_reference or name fields.
        :param params: dict/json
        :return: dict/json
        """
        domain = self._load_search_params(params)
        params.update({"domain": domain})
        return self._paginate_search(**params)

    def _load_search_params(self, params):
        """
        Based on params, build a domain to search on the PoS reference
        :param params: dict/json
        :return: list of tuple (Odoo domain)
        """
        domain = []
        value = params.get("value")
        if value:
            domain = [
                "|",
                ("pos_reference", "ilike", value),
                ("name", "ilike", value),
            ]
        return domain

    def _validator_get(self):
        return {}

    def _validator_search(self):
        """

        :return: dict
        """
        schema = self._default_validator_search()
        schema.pop("domain", False)
        schema.update({"value": {"type": "string", "required": False}})
        return schema

    def _return_schema_pos_validator(self):
        schema_pos = {
            "type": "dict",
            "schema": {
                "pos_id": {"type": "integer", "required": True},
                "name": {"type": "string"},
                "reference": {"type": "string", "nullable": True},
                "date": {"type": "string"},
                "amount_tax": {"type": "float"},
                "amount_untaxed": {"type": "float"},
                "amount_total": {"type": "float"},
                "partner": {
                    "type": "dict",
                    "schema": {
                        "partner_id": {"type": "integer", "required": True},
                        "name": {"type": "string"},
                    },
                },
                "lines": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": self._return_pos_order_line_schema(),
                    },
                },
            },
        }
        return schema_pos

    def _validator_return_get(self):
        schema = {"data": self._return_schema_pos_validator()}
        return schema

    def _return_pos_order_line_schema(self):
        schema = {
            "pos_line_id": {"type": "integer", "required": True},
            "discount": {"type": "float"},
            "quantity": {"type": "float"},
            "price_unit": {"type": "float"},
            "price_subtotal": {"type": "float"},
            "price_subtotal_incl": {"type": "float"},
            "product": {
                "type": "dict",
                "schema": {
                    "product_id": {"type": "integer", "required": True},
                    "name": {"type": "string"},
                    "sku": {"type": "string"},
                },
            },
            "taxes": {
                "type": "dict",
                "schema": {
                    "tax_id": {"type": "integer", "required": True},
                    "name": {"type": "string"},
                    "percentage": {"type": "float"},
                },
            },
        }
        return schema

    def _validator_return_search(self):
        schema_pos = self._return_schema_pos_validator()
        schema = {
            "size": {"type": "integer"},
            "data": {"type": "list", "schema": schema_pos},
        }
        return schema

    def _json_parser(self):
        """
        Parser for pos.order
        :return: list
        """
        to_parse = [
            "id:pos_id",
            "name",
            "pos_reference:reference",
            (
                "date_order:date",
                lambda rec, field_name, ts=fields.Datetime.to_string: ts(
                    rec[field_name]
                ),
            ),
            "amount_tax",
            "amount_total",
            ("partner_id:partner", ("id:partner_id", "name")),
            ("lines:pos_lines", self._json_parser_line()),
        ]
        return to_parse

    def _json_parser_line(self):
        """
        Parser for pos.order.line
        :return: list
        """
        to_parse = [
            "id:pos_line_id",
            "discount",
            "qty:quantity",
            "price_unit",
            "price_subtotal",
            "price_subtotal_incl",
            (
                "product_id:product",
                ("id:product_id", "name", "default_code:sku"),
            ),
            (
                "tax_ids_after_fiscal_position:taxes",
                ("id:tax_id", "name", "amount:percentage"),
            ),
        ]
        return to_parse

    def _to_json_pos_order(self, pos_order):
        """
        Jsonify related pos.order
        We have only to add recordset if the amount is different than 0.
        :param pos_order: pos.order recordset
        :return: dict
        """
        pos_parser = self._json_parser()
        precision = self.env["decimal.precision"].precision_get("Account")
        values = pos_order.jsonify(pos_parser, one=True)
        amount_untaxed = pos_order.amount_total - pos_order.amount_tax
        amount_untaxed = float_round(amount_untaxed, precision_rounding=precision)
        values.update({"amount_untaxed": amount_untaxed})
        return values

    def _to_json(self, pos_orders):
        """
        Jsonify the gift.list (multi) recordset
        :param pos_orders: gift.list recordset
        :return: list of dict
        """
        results = [self._to_json_pos_order(pos_order) for pos_order in pos_orders]
        return results
