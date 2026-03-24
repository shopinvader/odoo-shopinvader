from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from odoo.addons.shopinvader_api_cart.routers.cart import cart_helper
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale

quotation_cart_router = APIRouter(tags=["carts"])


class CartHelper(VirtualModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    def _request_quotation(self, uuid: UUID | None = None):
        sale = self._get_cart(uuid)
        sale.action_request_quotation()
        return sale


@quotation_cart_router.post("/{uuid}/request_quotation")
@quotation_cart_router.post("/current/request_quotation")
@quotation_cart_router.post("/request_quotation")
def request_quotation(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    uuid: UUID | None = None,
) -> Sale:
    return Sale.from_sale_order(helper._request_quotation(uuid))
