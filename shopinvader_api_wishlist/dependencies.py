# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from typing import Annotated

from fastapi import Depends

from odoo import api, fields, models
from odoo.exceptions import MissingError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.product_set.models.product_set_line import ProductSetLine
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale_wishlist.models.product_set import ProductSet
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter

from .schemas import (
    WishlistAddItemRequest,
    WishlistAddItemsToCartRequest,
    WishlistAddToCartRequest,
    WishlistCreateRequest,
    WishlistDeleteItemRequest,
    WishlistdMoveItemRequest,
    WishlistLineIdentifier,
    WishlistLines,
    WishlistReplaceItemRequest,
    WishlistSearchRequest,
    WishlistUpdateItemRequest,
    WishlistUpdateRequest,
)


class ShopinvaderApiWishlistRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_wishlist.router.helper"
    _description = "Shopinvader Api Wishlist Router Helper"

    partner = fields.Many2one("res.partner", string="Connected Partner", required=True)

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "!=", False),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[ProductSet]:
        return FilteredModelAdapter[ProductSet](self.env, self._get_domain_adapter())

    @property
    def model(self) -> ProductSet:
        return self.env["product.set"]

    def _get(self, record_id: int) -> ProductSet:
        return self.model_adapter.get(record_id)

    def _search(
        self, paging: Paging, params: WishlistSearchRequest
    ) -> tuple[int, ProductSet]:
        return self.model_adapter.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )

    def _create_wishlist(self, rqst: WishlistCreateRequest) -> ProductSet:
        return self.model.create(self._prepare_create_values(rqst))

    def _prepare_create_values(self, rqst: WishlistCreateRequest) -> dict:
        vals = rqst.to_product_set_vals(self.env)
        vals["partner_id"] = self.partner.id
        return vals

    def _update_wishlist(
        self, record_id: int, rqst: WishlistUpdateRequest
    ) -> ProductSet:
        product_set = self.model_adapter.get(record_id)
        product_set.write(self._prepare_update_value(rqst))
        return product_set

    def _prepare_update_value(self, rqst: WishlistUpdateRequest) -> dict:
        """On update, lines into the request are added to the existing lines"""
        return rqst.to_product_set_vals(self.env)

    def _add_to_cart(
        self, record_id: int, rqst: WishlistAddToCartRequest | None
    ) -> SaleOrder:
        uuid = rqst.uuid if rqst else None
        cart = self.env["sale.order"]._find_open_cart(self.partner.id, uuid)
        product_set = self._get(record_id)
        wizard = self.env["product.set.add"].create(
            {
                "order_id": cart.id,
                "product_set_id": product_set.id,
                "skip_existing_products": True,
            }
        )
        wizard.add_set()
        return cart

    def _add_items_to_cart(
        self, record_id: int, rqst: WishlistAddItemsToCartRequest
    ) -> SaleOrder:
        cart = self.env["sale.order"]._find_open_cart(self.partner.id, rqst.uuid)
        product_set = self._get(record_id)
        product_ids = [line.product_id for line in rqst.lines]
        lines = product_set.set_line_ids.filtered(
            lambda l, product_ids=product_ids: l.product_id.id in product_ids
        )
        wizard = self.env["product.set.add"].create(
            {
                "order_id": cart.id,
                "product_set_id": product_set.id,
                "skip_existing_products": True,
                "product_set_line_ids": lines,
            }
        )
        wizard.add_set()
        return cart

    def _add_items(
        self, record_id: int, rqst: WishlistLines[WishlistAddItemRequest]
    ) -> ProductSet:
        """
        Add items to the wishlist

        If a line refers to an existing one with the same product_id, the existing
        one is updated
        """
        return self._update_lines(record_id, rqst, raise_if_not_found=False)

    def _update_items(
        self, record_id: int, rqst: WishlistLines[WishlistUpdateItemRequest]
    ) -> ProductSet:
        """
        Update items to the wishlist

        If a line refers to an existing one with the same product_id, the existing
        one is updated
        """
        return self._update_lines(record_id, rqst, raise_if_not_found=True)

    def _update_lines(
        self,
        record_id: int,
        rqst: WishlistLines[WishlistAddItemRequest],
        raise_if_not_found: bool = True,
    ) -> ProductSet:
        """
        Update items in the wishlist

        If a line refers to an existing one with the same product_id, the existing
        one is updated
        """
        product_set = self._get(record_id)
        set_line_by_line_identifier = self._get_set_line_by_line_identifier(
            product_set, rqst.lines
        )
        update_vals = []
        for line in rqst.lines:
            if line in set_line_by_line_identifier:
                update_vals.append(
                    (
                        1,
                        set_line_by_line_identifier[line].id,
                        line.to_product_set_line_vals(self.env),
                    )
                )
            elif raise_if_not_found:
                raise MissingError(
                    f"Line with product_id {line.product_id} not found in "
                    f"wishlist {record_id}"
                )
            else:
                update_vals.append((0, 0, line.to_product_set_line_vals(self.env)))
        product_set.write({"set_line_ids": update_vals})
        # invalidate to force reordering
        product_set.invalidate_recordset(["set_line_ids"])
        return product_set

    def _get_set_line_by_line_identifier(
        self,
        product_set: ProductSet,
        indentifiers: list[WishlistLineIdentifier],
    ) -> dict[WishlistLineIdentifier:ProductSetLine]:
        set_line_by_product_id = {
            line.product_id.id: line for line in product_set.set_line_ids
        }
        return {
            identifier: set_line_by_product_id[identifier.product_id]
            for identifier in indentifiers
            if identifier.product_id in set_line_by_product_id
        }

    def _delete_items(
        self, record_id: int, rqst: WishlistLines[WishlistDeleteItemRequest]
    ) -> ProductSet:
        """
        Delete items from the wishlist

        If a line refers to an existing one with the same product_id, the existing
        one is deleted
        """
        product_set = self._get(record_id)
        set_line_by_line_identifier = self._get_set_line_by_line_identifier(
            product_set, rqst.lines
        )
        if len(set_line_by_line_identifier) != len(rqst.lines):
            for line in rqst.lines:
                if line not in set_line_by_line_identifier:
                    raise MissingError(
                        f"Line with product_id {line.product_id} not found in "
                        f"wishlist {record_id}"
                    )
        set_line_ids = [line.id for line in set_line_by_line_identifier.values()]
        self.env["product.set.line"].browse(set_line_ids).unlink()
        return product_set

    def _replace_items(
        self, record_id: int, rqst: WishlistLines[WishlistReplaceItemRequest]
    ) -> ProductSet:
        """
        Replace items in the wishlist

        """
        product_set = self._get(record_id)
        set_line_by_line_identifier = self._get_set_line_by_line_identifier(
            product_set, rqst.lines
        )
        if len(set_line_by_line_identifier) != len(rqst.lines):
            for line in rqst.lines:
                if line not in set_line_by_line_identifier:
                    raise MissingError(
                        f"Line with product_id {line.product_id} not found in "
                        f"wishlist {record_id}"
                    )
        update_vals = []
        for line in rqst.lines:
            update_vals.append(
                (
                    1,
                    set_line_by_line_identifier[line].id,
                    {"product_id": line.replacement_product_id},
                )
            )
        product_set.write(
            {
                "set_line_ids": update_vals,
            }
        )
        return product_set

    def _move_items(
        self, record_id: int, rqst: WishlistLines[WishlistdMoveItemRequest]
    ) -> ProductSet:
        """
        Move items from the wishlist to an other wishlist

        If a line refers to an existing one with the same product_id, the existing
        one is moved
        """
        product_set = self._get(record_id)
        set_line_by_line_identifier = self._get_set_line_by_line_identifier(
            product_set, rqst.lines
        )
        if len(set_line_by_line_identifier) != len(rqst.lines):
            for line in rqst.lines:
                if line not in set_line_by_line_identifier:
                    raise MissingError(
                        f"Line with product_id {line.product_id} not found in "
                        f"wishlist {record_id}"
                    )
        set_line_ids_by_destination = defaultdict(list)
        for rqst_line, set_line in set_line_by_line_identifier.items():
            set_line_ids_by_destination[rqst_line.move_to_wishlist_id].append(
                set_line.id
            )

        for destination_id, set_line_ids in set_line_ids_by_destination.items():
            # ensure destination exists
            self._get(destination_id)
            # write all lines at once
            self.env["product.set.line"].browse(set_line_ids).write(
                {"product_set_id": destination_id}
            )
        product_set.invalidate_recordset(["set_line_ids"])
        return product_set


def wishlist_router_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> ShopinvaderApiWishlistRouterHelper:
    return env["shopinvader_api_wishlist.router.helper"].new({"partner": partner})
