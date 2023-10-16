from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.fastapi.utils import FilteredDomainAdapter
from odoo.addons.shopinvader_schema_address.schemas import (
    DeliveryAddress,
    InvoicingAddress,
)

from ..schemas import (
    DeliveryAddressCreate,
    DeliveryAddressSearch,
    DeliveryAddressUpdate,
    InvoicingAddressCreate,
    InvoicingAddressSearch,
    InvoicingAddressUpdate,
)

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Invoicing addresses ---


@address_router.get("/addresses/invoicing")
def get_invoicing_addresses(
    params: Annotated[InvoicingAddressSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[InvoicingAddress]:
    """
    Get invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    count, addresses = env[
        "shopinvader_api_address.invoicing_address_router.helper"
    ]._search(paging, params)
    return PagedCollection[InvoicingAddress](
        count=count, items=[InvoicingAddress.from_res_partner(rec) for rec in addresses]
    )


@address_router.get("/addresses/invoicing/{address_id}")
def get_invoicing_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> InvoicingAddress:
    """
    Get invoicing address of authenticated user with specific address_id
    invoicing address corresponds to authenticated partner
    """
    address = env["shopinvader_api_address.invoicing_address_router.helper"]._get(
        address_id
    )
    return InvoicingAddress.from_res_partner(address)


@address_router.post("/addresses/invoicing", status_code=201)
def create_invoicing_address(
    data: InvoicingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> InvoicingAddress:
    """
    Create invoicing address
    Raise error since invoicing address is the authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = env["shopinvader_api_address.invoicing_address_router.helper"]._create(
        partner, vals
    )
    return InvoicingAddress.from_res_partner(address)


@address_router.post("/addresses/invoicing/{address_id}")
def update_invoicing_address(
    data: InvoicingAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> InvoicingAddress:
    """
    Update invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = (
        env["shopinvader_api_address.invoicing_address_router.helper"]
        .sudo()
        ._update(partner, vals, address_id)
    )
    return InvoicingAddress.from_res_partner(address)


# --- Delivery address ---


@address_router.get("/addresses/delivery")
def get_delivery_addresses(
    params: Annotated[DeliveryAddressSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[DeliveryAddress]:
    """
    Get delivery addresses of authenticated user
    Can be used to get every delivery address: /addresses/delivery
    """
    count, addresses = env[
        "shopinvader_api_address.delivery_address_router.helper"
    ]._search(paging, params)
    return PagedCollection[DeliveryAddress](
        count=count, items=[DeliveryAddress.from_res_partner(rec) for rec in addresses]
    )


@address_router.get("/addresses/delivery/{address_id}")
def get_delivery_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Get delivery addresses of authenticated user
    Can be used to get one specific address: /addresses/delivery/address_id
    """
    addresses = env["shopinvader_api_address.delivery_address_router.helper"]._get(
        address_id
    )
    return DeliveryAddress.from_res_partner(addresses)


@address_router.post("/addresses/delivery", status_code=201)
def create_delivery_address(
    data: DeliveryAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> DeliveryAddress:
    """
    Create delivery address of authenticated user
    """
    vals = data.to_res_partner_vals()
    address = env["shopinvader_api_address.delivery_address_router.helper"]._create(
        partner, vals
    )

    return DeliveryAddress.from_res_partner(address)


@address_router.post("/addresses/delivery/{address_id}")
def update_delivery_address(
    data: DeliveryAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Update delivery address of authenticated user
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = (
        env["shopinvader_api_address.delivery_address_router.helper"]
        .sudo()
        ._update(partner, vals, address_id)
    )
    return DeliveryAddress.from_res_partner(address)


@address_router.delete("/addresses/delivery/{address_id}")
def delete_delivery_address(
    address_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    """
    Delete delivery address of authenticated user
    Address will be archived.
    """

    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    env["shopinvader_api_address.delivery_address_router.helper"].sudo()._delete(
        partner, address_id
    )


class ShopinvaderApiBaseAddressRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_address.base_address_router.helper"
    _description = "Shopinvader Api Address Base Address Router Helper"

    def _create(self, partner, vals: dict) -> "ResPartner":
        vals = dict(vals, parent_id=partner.id, type=self._odoo_address_type)
        return self.env["res.partner"].create(vals)

    def _update(self, partner, vals: dict, address_id: int) -> "ResPartner":
        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                _(
                    "parent_id and type cannot be modified on"
                    " address, id: %(address_id)d",
                    address_id=address_id,
                )
            )

        address = self._get(address_id)

        # if address is already used, it is not possible to modify it
        self._ensure_address_not_used(address)

        # update_address
        address.write(vals)
        return address

    def _delete(self, partner, address_id: int) -> None:
        """
        Delete of delivery addresses will result to an archive
        """
        address = self._get(address_id)
        address.active = False

    def _domain_address_used(self, address):
        return [
            ("typology", "!=", "cart"),
            "|",
            ("partner_shipping_id", "=", address.id),
            ("partner_invoice_id", "=", address.id),
        ]

    def _ensure_address_not_used(self, address):
        """
        Check if the address is used on sale.order
        """
        address.ensure_one()
        domain = self._domain_address_used(address)
        sale_order = self.env["sale.order"].sudo().search(domain, limit=1)
        if len(sale_order) > 0:
            raise UserError(
                _(
                    "Can not update addresses(%(address_id)d)"
                    "because it is already used on confirmed sale order",
                    address_id=address.id,
                )
            )

    @property
    def partner_id(self):
        partner_id = self._context.get("authenticated_partner_id")
        if not partner_id:
            # This case should never happen as authenticated_partner is required
            # for this addresses route
            raise AccessError(_("Wrong Authentication"))
        else:
            return partner_id

    def _get(self, record_id):
        return self.adapter.get(record_id)

    def _search(self, paging, params):
        return self.adapter.search_with_count(
            params.to_odoo_domain(),
            limit=paging.limit,
            offset=paging.offset,
        )


# pylint: disable=consider-merging-classes-inherited


class ShopinvaderApiDeliveryAddressRouterHelper(models.Model):
    _inherit = "shopinvader_api_address.base_address_router.helper"
    _name = "shopinvader_api_address.delivery_address_router.helper"
    _description = "Shopinvader Api Address Delivery Address Router Helper"
    _odoo_address_type = "delivery"

    @property
    def adapter(self):
        return FilteredDomainAdapter(
            self.env["res.partner"],
            ["|", ("type", "=", "delivery"), ("id", "=", self.partner_id)],
        )


class ShopinvaderApiInvoicingAddressRouterHelper(models.Model):
    _inherit = "shopinvader_api_address.base_address_router.helper"
    _name = "shopinvader_api_address.invoicing_address_router.helper"
    _description = "Shopinvader Api Address Invoicing Address Router Helper"

    @property
    def adapter(self):
        return FilteredDomainAdapter(
            self.env["res.partner"],
            [("id", "=", self.partner_id)],
        )
