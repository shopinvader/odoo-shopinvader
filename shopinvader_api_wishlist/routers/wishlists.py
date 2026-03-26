# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields
from odoo.exceptions import MissingError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.product_set.models.product_set_line import ProductSetLine
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale_wishlist.models.product_set import ProductSet
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import (
    Wishlist,
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

wishlist_router = APIRouter(tags=["wishlists"])


class WishlistHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_wishlist.router.helper"
    _description = "Shopinvader Api Wishlist Router Helper"
    _model = "product.set"

    partner = fields.Many2one(
        "res.partner",
        string="Connected Partner",
        required=True,
    )

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "!=", False),
        ]

    def _prepare_values(self, rqst: WishlistCreateRequest) -> dict:
        vals = rqst.to_product_set_vals(self.env)
        return super()._prepare_values(vals)

    def _prepare_create_values(self, rqst: WishlistCreateRequest) -> dict:
        vals = super()._prepare_create_values(rqst)
        vals["partner_id"] = self.partner.id
        return vals

    def _add_to_cart(
        self, record_id: int, rqst: WishlistAddToCartRequest | None
    ) -> SaleOrder:
        uuid = rqst.uuid if rqst else None
        cart = self.env["sale.order"]._find_open_cart(self.partner.id, uuid)
        product_set = self.get(record_id)
        wizard = self.env["sale.product.set.wizard"].create(
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
        product_set = self.get(record_id)
        product_ids = [line.product_id for line in rqst.lines]
        lines = product_set.set_line_ids.filtered(
            lambda psl, product_ids=product_ids: psl.product_id.id in product_ids
        )
        wizard = self.env["sale.product.set.wizard"].create(
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
        product_set = self.get(record_id)
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
        product_set = self.get(record_id)
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
        product_set = self.get(record_id)
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
        product_set = self.get(record_id)
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
            self.get(destination_id)
            # write all lines at once
            self.env["product.set.line"].browse(set_line_ids).write(
                {"product_set_id": destination_id}
            )
        product_set.invalidate_recordset(["set_line_ids"])
        return product_set


def wishlist_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> WishlistHelper:
    return env["shopinvader_api_wishlist.router.helper"].new({"partner": partner})


@wishlist_router.get("/wishlists")
@wishlist_router.get("/wishlists/search")
def search(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    rqst: Annotated[WishlistSearchRequest, Depends()],
    paging_: Annotated[Paging, Depends(paging)],
) -> PagedCollection[Wishlist]:
    count, product_sets = helper.search_with_count(
        rqst.to_odoo_domain(helper.env),
        limit=paging_.limit,
        offset=paging_.offset,
    )
    return PagedCollection[Wishlist](
        count=count,
        items=[Wishlist.from_product_set(ps) for ps in product_sets],
    )


@wishlist_router.get("/wishlists/{_id}")
@wishlist_router.get("/wishlists/{_id}/get")
def get_info(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
) -> Wishlist:
    return Wishlist.from_product_set(helper.get(_id))


@wishlist_router.post("/wishlists/create", status_code=201)
@wishlist_router.post("/wishlists", status_code=201)
def create(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    rqst: WishlistCreateRequest,
) -> Wishlist:
    return Wishlist.from_product_set(helper.create(rqst))


@wishlist_router.post("/wishlists/{_id}/update")
@wishlist_router.put("/wishlists/{_id}")
def update(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistUpdateRequest,
) -> Wishlist:
    """This method is used to update a wishlist.

    Pay attention that lines given in the request will be added to the existing
    lines.

    If you want to replace the lines, use the replace_items method.
    If you want to delete the lines, use the delete_items method.
    ...
    """
    return Wishlist.from_product_set(helper.write(_id, rqst))


@wishlist_router.delete("/wishlists/{_id}")
def delete(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
) -> Wishlist:
    return helper.unlink(
        _id,
        lambda product_set: Wishlist.from_product_set(odoo_rec=product_set),
    )


@wishlist_router.post("/wishlists/{_id}/add_to_cart")
def add_to_cart(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistAddToCartRequest | None = None,
) -> Sale:
    cart = helper._add_to_cart(_id, rqst)
    return Sale.from_sale_order(cart)


@wishlist_router.post("/wishlists/{_id}/add_items_to_cart")
def add_items_to_cart(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistAddItemsToCartRequest,
) -> Sale:
    cart = helper._add_items_to_cart(_id, rqst)
    return Sale.from_sale_order(cart)


@wishlist_router.post("/wishlists/{_id}/add_item")
def add_item(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    item: WishlistAddItemRequest,
) -> Wishlist:
    """
    Add a new item to the wishlist

    If rqst refers to an existing line with the same product_id, the existing
    one is updated
    """
    product_set = helper._add_items(
        _id, WishlistLines[WishlistAddItemRequest](lines=[item])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/add_items")
def add_items(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistLines[WishlistAddItemRequest],
) -> Wishlist:
    """
    Add items to the wishlist

    If a line refers to an existing one with the same product_id, the existing
    one is updated
    """

    product_set = helper._add_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/update_item")
def update_item(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistUpdateItemRequest,
) -> Wishlist:
    """
    Update an item in the wishlist

    If no line is found with the same product_id, an error is raised
    """
    product_set = helper._update_items(
        _id, WishlistLines[WishlistUpdateItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/update_items")
def update_items(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistLines[WishlistUpdateItemRequest],
) -> Wishlist:
    """
    Update items in the wishlist

    If a line does not refer to an existing one with the same product_id,
    an error is raised
    """
    product_set = helper._update_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/delete_item")
def delete_item(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistDeleteItemRequest,
) -> Wishlist:
    product_set = helper._delete_items(
        _id, WishlistLines[WishlistDeleteItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/delete_items")
def delete_items(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistLines[WishlistDeleteItemRequest],
) -> Wishlist:
    product_set = helper._delete_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/move_item")
def move_item(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistdMoveItemRequest,
) -> Wishlist:
    product_set = helper._move_items(
        _id, WishlistLines[WishlistdMoveItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/move_items")
def move_items(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistLines[WishlistdMoveItemRequest],
) -> Wishlist:
    product_set = helper._move_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/replace_item")
def replace_item(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistReplaceItemRequest,
) -> Wishlist:
    product_set = helper._replace_items(
        _id, WishlistLines[WishlistReplaceItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/replace_items")
def replace_items(
    helper: Annotated[WishlistHelper, Depends(wishlist_helper)],
    _id: int,
    rqst: WishlistLines[WishlistReplaceItemRequest],
) -> Wishlist:
    product_set = helper._replace_items(_id, rqst)
    return Wishlist.from_product_set(product_set)
