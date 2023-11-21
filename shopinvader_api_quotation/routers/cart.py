from typing import Annotated

from fastapi import Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale


@cart_router.post("/{uuid}/request_quotation")
def request_quotation(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: str | None = None,
) -> Sale:
    sale = env["sale.order"]._find_open_cart(partner.id, uuid)
    sale.action_request_quotation()

    return Sale.from_sale_order(sale)
