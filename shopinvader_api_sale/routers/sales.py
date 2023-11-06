# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, models

from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.fastapi.utils import FilteredDomainAdapter
from odoo.addons.shopinvader_schema_sale.schemas import Sale, SaleSearch

sale_router = APIRouter(tags=["sales"])


@sale_router.get("/sales")
def search(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
) -> PagedCollection[Sale]:
    """Get / search sale orders. The list contains only sale orders from the
    authenticated user"""
    count, orders = env["shopinvader_api_sale.sales_router.helper"]._search(
        paging, params
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@sale_router.get("/sales/{sale_id}")
def get(
    sale_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
) -> Sale:
    """
    Get sale order of authenticated user with specific sale_id
    """
    return Sale.from_sale_order(
        env["shopinvader_api_sale.sales_router.helper"]._get(sale_id)
    )


class ShopinvaderApiSaleSalesRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_sale.sales_router.helper"
    _description = "Shopinvader Api Sale Service Helper"

    @property
    def filtered_model(self):
        return FilteredDomainAdapter(
            self.env["sale.order"], [("typology", "=", "sale")]
        )

    def _get(self, record_id):
        return self.filtered_model.get(record_id)

    def _search(self, paging, params):
        return self.filtered_model.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )
