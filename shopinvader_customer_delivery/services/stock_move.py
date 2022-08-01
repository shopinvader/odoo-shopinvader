# Copyright 2022 Akretion (<https://akretion.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.osv import expression

from odoo.addons.component.core import Component


class DeliveryMoveService(Component):
    """Service for getting information on stock.picking"""

    _inherit = ["base.shopinvader.service", "abstract.shopinvader.download"]
    _name = "shopinvader.delivery.move.service"
    _usage = "delivery_moves"
    _expose_model = "stock.move"
    _description = __doc__

    def search(self, **params):
        """
        Get every delivery products related to logged user
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def _validator_search(self):
        """
        Validator for the search
        :return: dict
        """
        validator = self._default_validator_search()
        validator.pop("domain", {})
        validator.pop("scope", {})
        return validator

    def _get_stock_move_schema(self):
        """

        :return: dict
        """
        schema = {
            "delivery_move_id": {"type": "integer"},
            "delivery_move_state": {"type": "string", "nullable": True},
            "delivery_product_qty": {"type": "float", "nullable": True},
            "delivery_product_uom_id": {"type": "string", "nullable": True},
            "delivery_schedule_date": {"type": "string", "nullable": True},
            "product": {
                "type": "dict",
                "nullable": True,
                "schema": {
                    "product_id": {"type": "string"},
                    "template_id": {"type": "string"},
                    "name": {"type": "string"},
                    "default_code": {"type": "string"},
                },
            },
            "sale": {
                "type": "dict",
                "nullable": True,
                "schema": {
                    "sale_id": {"type": "integer"},
                    "state": {"type": "string"},
                    "date_order": {"type": "string", "nullable": True},
                    "name": {"type": "string", "nullable": True},
                },
            },
        }
        return schema

    def _get_allowed_stock_move_domain(self):
        """Domain to filter stock move.

        :return: list of tuples
        """
        states = ["waiting", "confirmed", "partially_available", "assigned"]
        # todo add method to backend to get visible states
        domain = [
            ("picking_id.picking_type_id.code", "=", "outgoing"),
        ]
        if states:
            domain.append(("state", "in", states))
        return domain

    def _validator_return_search(self):
        """
        Output validator for the search
        :return: dict
        """
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._get_stock_move_schema(),
                },
            },
        }
        return schema

    def _get_parser_stock_move(self):
        """
        Get the parser of stock.move
        :return: list
        """
        to_parse = [
            "id:delivery_move_id",
            "state:delivery_move_state",
            "product_uom_qty:delivery_product_qty",
            "product_uom:delivery_product_uom_id",
            "date:delivery_schedule_date",
        ]
        return to_parse

    def _get_parser_product(self):
        """
        Get the parser of product.product
        :return: list
        """
        to_parse = [
            "id:product_id",
            "product_tmpl_id:template_id",
            "name",
            "default_code",
        ]
        return to_parse

    def _add_product_info(self, stok_move):
        """
        Add info about the related product (using product_id field).
        :param picking: stock.move
        :return: dict
        """
        sale_order = stok_move.product_id
        if not sale_order:
            return {}
        parser = self._get_parser_sale_order()
        values = sale_order.jsonify(parser, one=True)
        return values

    def _get_parser_sale_order(self):
        """
        Get the parser of sale.order
        :return: list
        """
        to_parse = [
            "id:sale_id",
            "name",
            "state",
            "amount_total",
            "date_order",
        ]
        return to_parse

    def _add_sale_order_info(self, picking):
        """
        Add info about the related sale order (using sale_id field).
        :param picking: stock.move
        :return: dict
        """
        sale_order = picking.sale_id
        if not sale_order:
            return {}
        parser = self._get_parser_sale_order()
        values = sale_order.jsonify(parser, one=True)
        return values

    def _to_json_stock_move(self, stok_move):
        stok_move.ensure_one()
        parser = self._get_parser_stock_move()
        values = stok_move.jsonify(parser, one=True)
        picking = stok_move.picking_id
        values.update(
            {
                "sale": self._add_sale_order_info(picking),
                "product": self._add_product_info(stok_move),
            }
        )
        return values

    def _to_json(self, stok_move):
        res = []
        for move in stok_move:
            res.append(self._to_json_stock_move(move))
        return res

    def _get_base_search_domain(self):
        """Get every stock.move OUT related to current user.

        If the current user is the anonymous one, it'll return an invalid
        domain (to have 0 picking as result)
        :return:
        """
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        sale_service = self.component(usage="sales")
        sale_domain = sale_service._get_base_search_domain()
        print(sale_domain)
        sales = self.env[sale_service._expose_model].search(sale_domain)
        print([("sale_id", "in", sales.ids)] + self._get_allowed_stock_move_domain())
        return [
            ("picking_id.sale_id", "in", sales.ids)
        ] + self._get_allowed_stock_move_domain()
