# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import authenticated_partner, odoo_env

from ..schemas.price_get import PriceGetInput
from ..schemas.product import ProductPrice

customer_price_router = APIRouter(tags=["customer_price"])


@customer_price_router.post("/customer_price")
async def price_get(
    data: PriceGetInput,
    env: Annotated[Environment, Depends(odoo_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Dict[int, ProductPrice]:  # noqa: B008
    """Get the list of current customer prices for given products.
    
    :return: Mapping {$prod_id: $price_info}.
    """
    products = env["product.product"].sudo().browse(data.ids).exists()
    pricelist = partner.sudo().property_product_pricelist
    if data.pricelist_id:
        pricelist = env["product.pricelist"].sudo().browse(data.pricelist_id)
    return ProductPrice.from_products(products, pricelist=pricelist)
