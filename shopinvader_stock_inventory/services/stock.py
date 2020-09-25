# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from datetime import datetime

from odoo import fields
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class ProductService(Component):
    _inherit = ["base.shopinvader.service"]
    _name = "shopinvader.stock.service"
    _usage = "stock"
    _expose_model = "product.product"

    def get(self, _id=None, **params):
        """Return the product specified by _id."""
        if _id:
            return self._to_json_one(self._get(_id))
        else:
            return self.search(**params)

    def search(self, **params):
        """Returns all product or all product in category."""
        params["domain"] = []
        if "per_page" not in params:
            # Return all items by default
            params["per_page"] = 0
        if "category_id" in params:
            params["domain"].append(("categ_id", "=", params["category_id"]))
            params.pop("category_id")
        if "ean" in params:
            params["domain"].append(("barcode", "=", params["ean"]))
            params.pop("ean")
        if "date" in params:
            params["domain"].append(
                ("write_date", ">=", fields.Datetime.to_string(params["date"]))
            )
            params.pop("date")
        return self._paginate_search(**params)

    def _validator_search(self):
        schema = {
            "category_id": {"coerce": to_int, "type": "integer"},
            "ean": {"type": "string"},
            "date": {"coerce": self._convert_to_time(), "type": "datetime"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
        }
        return schema

    def _convert_to_time(self):
        return lambda rec: datetime.strptime(rec, "%d/%m/%Y %H:%M:%S")

    def _get_base_search_domain(self):
        """ By default only salable products are shown by the service."""
        return [("sale_ok", "=", True), ("type", "=", "product")]

    def _to_json(self, records):
        res = []
        for product in records:
            res.append(self._to_json_product(product))
        return res

    def _to_json_one(self, records):
        return self._to_json(fields.first(records))[0]

    def _json_parser(self):
        return [
            "id",
            "name",
            "default_code",
            "list_price:price",
            ("ean", lambda rec, fname: rec.barcode or ""),
            "qty_available",
            ("attribute_line_ids:attributes", self._json_parser_attributes()),
        ]

    def _json_parser_attributes(self):
        return [
            ("attribute_id:attribute", ["id", "name"]),
            ("value_ids:values", ["id", "name"]),
        ]

    def _to_json_product(self, product):
        product.ensure_one()
        parser = self._json_parser()
        values = product.jsonify(parser)[0]
        category = product.categ_id
        values.update(
            {
                "category": {
                    "name": category.name or "",
                    "id": category.get_external_id().get(category.id, ""),
                },
                "xml_id": product.get_external_id().get(product.id, ""),
            }
        )
        return values
