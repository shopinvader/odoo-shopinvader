from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import models
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.fastapi.utils import FilteredDomainAdapter
from odoo.addons.shopinvader_schema_sale.schemas.sale_order import Sale, SaleSearch

# create a router
quotation_router = APIRouter(tags=["quotations"])


@quotation_router.get("/quotations/{quotation_id}")
def get(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: int | None = None,
) -> Sale | None:
    return Sale.from_sale_order(
        env["shopinvader_api_quotation.quotations_router.helper"]._get(quotation_id)
    )


@quotation_router.get("/quotations/{quotation_id}/confirm", status_code=200)
def confirm_quotation(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: int | None = None,
) -> None:
    order = env["shopinvader_api_quotation.quotations_router.helper"]._confirm(
        quotation_id
    )
    # env["sale.order"]._confirm(order)
    # order.action_confirm()
    return Sale.from_sale_order(order)


@quotation_router.get("/quotations", status_code=200)
def search_quotation(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Sale]:
    count, orders = env["shopinvader_api_quotation.quotations_router.helper"]._search(
        paging, params
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


class ShopinvaderApiQuotationquotationsRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_quotation.quotations_router.helper"
    _description = "Shopinvader Api Quotation Service Helper"

    @property
    def adapter(self):
        return FilteredDomainAdapter(
            self.env["sale.order"], [("typology", "=", "quotation")]
        )

    def _get(self, record_id):
        return self.adapter.get(record_id)

    def _search(self, paging, params):
        return self.adapter.search_with_count(
            params.to_odoo_domain(),
            limit=paging.limit,
            offset=paging.offset,
        )

    def _confirm(self, quotation):
        order = self._get(quotation)
        order.action_confirm()
        return order
