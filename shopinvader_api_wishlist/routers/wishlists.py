# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends

from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import paging
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..dependencies import ShopinvaderApiWishlistRouterHelper, wishlist_router_helper
from ..schemas import (
    Wishlist,
    WishlistAddItemRequest,
    WishlistAddItemsToCartRequest,
    WishlistAddToCartRequest,
    WishlistCreateRequest,
    WishlistDeleteItemRequest,
    WishlistdMoveItemRequest,
    WishlistLines,
    WishlistReplaceItemRequest,
    WishlistSearchRequest,
    WishlistUpdateItemRequest,
    WishlistUpdateRequest,
)

wishlist_router = APIRouter(tags=["wishlists"])


@wishlist_router.get("/wishlists/")
@wishlist_router.get("/wishlists/search/")
def search(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    rqst: Annotated[WishlistSearchRequest, Depends()],
    paging_: Annotated[Paging, Depends(paging)],
) -> PagedCollection[Wishlist]:
    count, product_sets = wishlist_router_helper._search(paging_, rqst)
    return PagedCollection[Wishlist](
        count=count,
        items=[Wishlist.from_product_set(ps) for ps in product_sets],
    )


@wishlist_router.get("/wishlists/{_id}")
@wishlist_router.get("/wishlists/{_id}/get")
def get_info(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
) -> Wishlist:
    product_set = wishlist_router_helper._get(_id)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/create/", status_code=201)
@wishlist_router.post("/wishlists/", status_code=201)
def create(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    rqst: WishlistCreateRequest,
) -> Wishlist:
    product_set = wishlist_router_helper._create_wishlist(rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/update")
@wishlist_router.put("/wishlists/{_id}")
def update(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
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
    product_set = wishlist_router_helper._update_wishlist(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.delete("/wishlists/{_id}", status_code=204)
def delete(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
) -> None:
    product_set = wishlist_router_helper._get(_id)
    product_set.unlink()


@wishlist_router.post("/wishlists/{_id}/add_to_cart")
def add_to_cart(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistAddToCartRequest | None = None,
) -> Sale:
    cart = wishlist_router_helper._add_to_cart(_id, rqst)
    return Sale.from_sale_order(cart)


@wishlist_router.post("/wishlists/{_id}/add_items_to_cart")
def add_items_to_cart(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistAddItemsToCartRequest,
) -> Sale:
    cart = wishlist_router_helper._add_items_to_cart(_id, rqst)
    return Sale.from_sale_order(cart)


@wishlist_router.post("/wishlists/{_id}/add_item")
def add_item(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    item: WishlistAddItemRequest,
) -> Wishlist:
    """
    Add a new item to the wishlist

    If rqst refers to an existing line with the same product_id, the existing
    one is updated
    """
    product_set = wishlist_router_helper._add_items(
        _id, WishlistLines[WishlistAddItemRequest](lines=[item])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/add_items")
def add_items(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistLines[WishlistAddItemRequest],
) -> Wishlist:
    """
    Add items to the wishlist

    If a line refers to an existing one with the same product_id, the existing
    one is updated
    """

    product_set = wishlist_router_helper._add_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/update_item")
def update_item(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistUpdateItemRequest,
) -> Wishlist:
    """
    Update an item in the wishlist

    If no line is found with the same product_id, an error is raised
    """
    product_set = wishlist_router_helper._update_items(
        _id, WishlistLines[WishlistUpdateItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/update_items")
def update_items(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistLines[WishlistUpdateItemRequest],
) -> Wishlist:
    """
    Update items in the wishlist

    If a line does not refer to an existing one with the same product_id, an error is raised
    """
    product_set = wishlist_router_helper._update_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/delete_item")
def delete_item(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistDeleteItemRequest,
) -> Wishlist:
    product_set = wishlist_router_helper._delete_items(
        _id, WishlistLines[WishlistDeleteItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/delete_items")
def delete_items(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistLines[WishlistDeleteItemRequest],
) -> Wishlist:
    product_set = wishlist_router_helper._delete_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/move_item")
def move_item(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistdMoveItemRequest,
) -> Wishlist:
    product_set = wishlist_router_helper._move_items(
        _id, WishlistLines[WishlistdMoveItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/move_items")
def move_items(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistLines[WishlistdMoveItemRequest],
) -> Wishlist:
    product_set = wishlist_router_helper._move_items(_id, rqst)
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/replace_item/")
def replace_item(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistReplaceItemRequest,
) -> Wishlist:
    product_set = wishlist_router_helper._replace_items(
        _id, WishlistLines[WishlistReplaceItemRequest](lines=[rqst])
    )
    return Wishlist.from_product_set(product_set)


@wishlist_router.post("/wishlists/{_id}/replace_items/")
def replace_items(
    wishlist_router_helper: Annotated[
        ShopinvaderApiWishlistRouterHelper, Depends(wishlist_router_helper)
    ],
    _id: int,
    rqst: WishlistLines[WishlistReplaceItemRequest],
) -> Wishlist:
    product_set = wishlist_router_helper._replace_items(_id, rqst)
    return Wishlist.from_product_set(product_set)
