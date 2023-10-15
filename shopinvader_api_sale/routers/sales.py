# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import SaleSearch

sale_router = APIRouter(tags=["sales"])


@sale_router.get("/sales")
def search(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
) -> PagedCollection[Sale]:
    """Get the list of sale orders."""
    count, orders = env["shopinvader_api_sale.service.sales"]._search(paging, params)
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@sale_router.get("/sales/{sale_id}")
def get(
    sale_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
) -> Sale:
    """
    Get sale order of authenticated user with specific sale_id
    sale corresponds to authenticated partner
    """
    return Sale.from_sale_order(env["shopinvader_api_sale.service.sales"]._get(sale_id))


class ShopinvaderApiServiceSales(models.AbstractModel):
    _inherit = "fastapi.service.base"
    _name = "shopinvader_api_sale.service.sales"
    _description = "Shopinvader Api Sale Service Helper"
    _odoo_model = "sale.order"

    @property
    def _odoo_model_domain_restrict(self):
        return [("typology", "=", "sale")]

    def _convert_search_params_to_domain(self, params):
        if params.name:
            return [("name", "ilike", self.name)]
        else:
            return []
