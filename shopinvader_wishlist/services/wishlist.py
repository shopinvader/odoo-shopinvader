# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, exceptions
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv import expression
from werkzeug.exceptions import NotFound


class WishlistService(Component):
    """Shopinvader service to manage current user's wishlists.
    """

    _name = "shopinvader.wishlist.service"
    _inherit = "base.shopinvader.service"
    _usage = "wishlist"
    _expose_model = "product.set"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        record = self._get(_id)
        return self._to_json_one(record)

    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        if not self._is_logged_in():
            # TODO: is there any way to control this in the REST API?
            raise exceptions.UserError(
                _("Must be authenticated to create a wishlist")
            )
        vals = self._prepare_params(params.copy())
        record = self.env[self._expose_model].create(vals)
        self._post_create(record)
        return {"data": self._to_json_one(record)}

    def update(self, _id, **params):
        record = self._get(_id)
        record.write(self._prepare_params(params.copy(), mode="update"))
        self._post_update(record)
        return self.search()

    def delete(self, _id):
        self._get(_id).unlink()
        return self.search()

    def add_to_cart(self, _id):
        record = self._get(_id)
        cart_service = self.component(usage="cart")
        cart = cart_service._get()
        wizard = self.env["product.set.add"].create(
            {
                "order_id": cart.id,
                "partner_id": self.partner_user.id,
                "product_set_id": record.id,
                "skip_existing_products": True,
            }
        )
        wizard.add_set()
        # return new cart
        return cart_service._to_json(cart)

    def add_items(self, _id, **params):
        record = self._get(_id)
        self._add_items(record, params)
        return self._to_json_one(record)

    def update_items(self, _id, **params):
        record = self._get(_id)
        self._update_items(record, params)
        return self._to_json_one(record)

    def delete_items(self, _id, **params):
        record = self._get(_id)
        self._delete_items(record, params)
        return self._to_json_one(record)

    def move_items(self, _id, **params):
        record = self._get(_id)
        self._move_items(record, params)
        return self._to_json_one(record)

    def _post_create(self, record):
        pass

    def _post_update(self, record):
        pass

    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            "id": {"coerce": to_int, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_create(self):
        return {
            "name": {"type": "string", "required": True},
            "ref": {"type": "string", "required": True, "empty": False},
            "partner_id": {
                "type": "integer",
                "coerce": to_int,
                "nullable": True,
            },
            "typology": {"type": "string", "nullable": True},
            "lines": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": self._validator_line_schema(),
                },
            },
        }

    def _validator_line_schema(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "quantity": {"coerce": float, "type": "float", "default": 1.0},
            "sequence": {
                "coerce": int,
                "type": "integer",
                "required": False,
                "default": 0,
            },
        }

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _validator_add_to_cart(self):
        return {"id": {"coerce": to_int, "type": "integer"}}

    def _validator_add_items(self):
        return {
            "lines": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": self._validator_add_item(),
                },
            }
        }

    def _validator_add_item(self):
        return self._validator_line_schema()

    def _validator_update_items(self):
        return self._validator_add_items()

    def _validator_move_items(self):
        return {
            "lines": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": self._validator_move_item(),
                },
            }
        }

    def _validator_move_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "move_to_wishlist_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
        }

    def _validator_delete_items(self):
        return {
            "lines": {
                "type": "list",
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": self._validator_delete_item(),
                },
            }
        }

    def _validator_delete_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            }
        }

    def _get_base_search_domain(self):
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return self._default_domain_for_partner_records()

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            if not params.get("partner_id"):
                params["partner_id"] = self.partner_user.id
        if not params.get("typology"):
            params["typology"] = "wishlist"
        record = self.env[self._expose_model].browse()  # no record yet
        params["set_line_ids"] = [
            (0, 0, self._prepare_item(record, line))
            for line in params.pop("lines", [])
        ]
        return params

    def _to_json(self, records):
        return records.jsonify(self._json_parser())

    def _to_json_one(self, records):
        # This works only here... see `_update_item` :/
        records.set_line_ids.invalidate_cache()
        values = self._to_json(records)
        if len(records) == 1:
            values = values[0]
        return values

    def _json_parser(self):
        return [
            "id",
            "name",
            "typology",
            "ref",
            ("partner_id:partner", ["id", "name"]),
            ("set_line_ids:lines", self._json_parser_line()),
        ]

    def _json_parser_line(self):
        return [
            "id",
            "sequence",
            "quantity",
            ("shopinvader_variant_id:product", self._json_parser_product()),
        ]

    def _json_parser_product(self):
        # TODO: might be better to use product's index data
        # to avoid further computation, conversion
        # and mismatch between indexed data and current data.
        parser = [
            "id",
            "name",
            "default_code:sku",
            "url_key",
            "price",
            "object_id:objectID",
        ]
        if "images" in self.env["shopinvader.variant"]._fields:
            # avoid hard dependency on shopinvader_image
            parser.append("images")
        return parser

    def _get_existing_line(self, record, params, raise_if_not_found=False):
        product_id = params["product_id"]
        line = record.get_line_by_product(product_id=product_id)
        if not line and raise_if_not_found:
            raise NotFound(
                "No product found with id %s" % params["product_id"]
            )
        return line

    def _update_lines(self, record, lines, raise_if_not_found=False):
        new_items = []
        for item_params in lines:
            existing = self._get_existing_line(
                record, item_params, raise_if_not_found=raise_if_not_found
            )
            if existing:
                item_update_params = self._prepare_item(record, item_params)
                # prevent move or prod change on update
                item_update_params = {
                    k: v
                    for k, v in item_update_params.items()
                    if k not in ("product_set_id", "product_id")
                }
                existing.write(item_update_params)
            else:
                new_items.append(item_params)
        values = [
            (0, 0, self._prepare_item(record, item_params))
            for item_params in new_items
        ]
        if values:
            record.write({"set_line_ids": values})
        # TODO: WTF?? Cache on sequence is not invalidated.
        # And calling this does not work here, must be called in `_to_json_one`.
        # record.set_line_ids.invalidate_cache()
        # flush does not work neither
        # record.set_line_ids.flush()

    def _add_items(self, record, params):
        self._update_lines(record, params["lines"])

    def _update_items(self, record, params):
        self._update_lines(record, params["lines"], raise_if_not_found=True)

    def _move_items(self, record, params):
        # group lines by destination
        by_destination = defaultdict(self.env["product.set.line"].browse)
        to_delete = self.env["product.set.line"].browse()
        for item_params in params["lines"]:
            existing = self._get_existing_line(
                record, item_params, raise_if_not_found=True
            )
            to_delete |= existing
            by_destination[item_params["move_to_wishlist_id"]] += existing

        # move all lines to each destination at once
        for move_to_id, move_to_items in by_destination.items():
            move_to_wl = self._get(move_to_id)
            lines = move_to_items.read(
                ["product_id", "quantity", "sequence"], load="_classic_write"
            )
            values = [
                (0, 0, self._prepare_item(move_to_wl, line)) for line in lines
            ]
            move_to_wl.write({"set_line_ids": values})
        # delete all old records
        to_delete.unlink()

    def _prepare_item(self, record, params):
        return {
            "product_set_id": record.id,
            "product_id": params["product_id"],
            "quantity": params.get("quantity") or 1,
            "sequence": params.get("sequence") or 0,
        }

    def _delete_items(self, record, params):
        to_delete = self.env["product.set.line"].browse()
        for item_params in params["lines"]:
            existing = self._get_existing_line(
                record, item_params, raise_if_not_found=True
            )
            to_delete |= existing
        to_delete.unlink()
