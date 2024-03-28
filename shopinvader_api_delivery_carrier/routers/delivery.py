# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter
from odoo.addons.stock.models.stock_picking import Picking as StockPicking

from ..schemas import Picking

delivery_router = APIRouter(tags=["deliveries"])


@delivery_router.get("/deliveries")
def search(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    paging_: Annotated[Paging, Depends(paging)],
) -> PagedCollection[Picking]:
    count, pickings = (
        env["shopinvader_api_delivery_carrier.delivery_router.helper"]
        .new({"partner": partner})
        ._search(paging_)
    )
    return PagedCollection[Picking](
        count=count, items=[Picking.from_picking(picking) for picking in pickings]
    )


class ShopinvaderApiDeliveryRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_delivery_carrier.delivery_router.helper"
    _description = "ShopInvader API Delivery Router Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        sales = self.env["sale.order"].search(
            [("typology", "=", "sale"), ("partner_id", "=", self.partner.id)]
        )
        return [
            ("sale_id", "in", sales.ids),
            ("picking_type_id.code", "=", "outgoing"),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[StockPicking]:
        return FilteredModelAdapter[StockPicking](self.env, self._get_domain_adapter())

    def _search(self, paging) -> tuple[int, StockPicking]:
        return self.model_adapter.search_with_count(
            [],
            limit=paging.limit,
            offset=paging.offset,
        )
