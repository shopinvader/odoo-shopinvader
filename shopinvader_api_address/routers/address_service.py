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
from odoo.addons.shopinvader_schema_address.schemas import (
    BillingAddress,
    ShippingAddress,
)

from ..schemas import (
    BillingAddressCreate,
    BillingAddressSearch,
    BillingAddressUpdate,
    ShippingAddressCreate,
    ShippingAddressSearch,
    ShippingAddressUpdate,
)

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Billing addresses ---


@address_router.get("/addresses/billing")
def get_billing_addresses(
    params: Annotated[BillingAddressSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[BillingAddress]:
    """
    Get billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    count, addresses = env["shopinvader_api_address.service.invoicing_address"]._search(
        paging, params
    )
    return PagedCollection[BillingAddress](
        count=count, items=[BillingAddress.from_res_partner(rec) for rec in addresses]
    )


@address_router.get("/addresses/billing/{address_id}")
def get_billing_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> BillingAddress:
    """
    Get billing address of authenticated user with specific address_id
    billing address corresponds to authenticated partner
    """
    address = env["shopinvader_api_address.service.invoicing_address"]._get(address_id)
    return BillingAddress.from_res_partner(address)


@address_router.post("/addresses/billing", status_code=201)
def create_billing_address(
    data: BillingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> BillingAddress:
    """
    Create billing address
    Raise error since billing address is the authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = env["shopinvader_api_address.service.invoicing_address"]._create(
        partner, vals
    )
    return BillingAddress.from_res_partner(address)


@address_router.post("/addresses/billing/{address_id}")
def update_billing_address(
    data: BillingAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> BillingAddress:
    """
    Update billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = (
        env["shopinvader_api_address.service.invoicing_address"]
        .sudo()
        ._update(partner, vals, address_id)
    )
    return BillingAddress.from_res_partner(address)


# --- Shipping address ---


@address_router.get("/addresses/shipping")
def get_shipping_addresses(
    params: Annotated[ShippingAddressSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[ShippingAddress]:
    """
    Get shipping addresses of authenticated user
    Can be used to get every shipping address: /addresses/shipping
    """
    count, addresses = env["shopinvader_api_address.service.delivery_address"]._search(
        paging, params
    )
    return PagedCollection[ShippingAddress](
        count=count, items=[ShippingAddress.from_res_partner(rec) for rec in addresses]
    )


@address_router.get("/addresses/shipping/{address_id}")
def get_shipping_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> ShippingAddress:
    """
    Get shipping addresses of authenticated user
    Can be used to get one specific address: /addresses/shipping/address_id
    """
    addresses = env["shopinvader_api_address.service.delivery_address"]._get(address_id)
    return ShippingAddress.from_res_partner(addresses)


@address_router.post("/addresses/shipping", status_code=201)
def create_shipping_address(
    data: ShippingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShippingAddress:
    """
    Create shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    address = env["shopinvader_api_address.service.delivery_address"]._create(
        partner, vals
    )

    return ShippingAddress.from_res_partner(address)


@address_router.post("/addresses/shipping/{address_id}")
def update_shipping_address(
    data: ShippingAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> ShippingAddress:
    """
    Update shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = (
        env["shopinvader_api_address.service.delivery_address"]
        .sudo()
        ._update(partner, vals, address_id)
    )
    return ShippingAddress.from_res_partner(address)


@address_router.delete("/addresses/shipping/{address_id}")
def delete_shipping_address(
    address_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    """
    Delete shipping address of authenticated user
    Address will be archived.
    """

    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    env["shopinvader_api_address.service.delivery_address"].sudo()._delete(
        partner, address_id
    )


class ShopinvaderApiServiceBaseAddress(models.AbstractModel):
    _inherit = "fastapi.service.base"
    _name = "shopinvader_api_address.service.base_address"
    _description = "Shopinvader Api Address Service Base Address"
    _odoo_model = "res.partner"
    _odoo_address_type = None

    def _convert_search_params_to_domain(self, params):
        if params.name:
            return [("name", "ilike", self.name)]
        else:
            return []

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
        Delete of shipping addresses will result to an archive
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


# pylint: disable=consider-merging-classes-inherited


class ShopinvaderApiServiceDeliveryAddress(models.Model):
    _inherit = "shopinvader_api_address.service.base_address"
    _name = "shopinvader_api_address.service.delivery_address"
    _description = "Shopinvader Api Address Service Delivery Address"
    _odoo_address_type = "delivery"

    @property
    def _odoo_model_domain_restrict(self):
        return [
            "|",
            ("type", "=", self._odoo_address_type),
            ("id", "=", self.partner_id),
        ]


class ShopinvaderApiServiceInvoicingAddress(models.Model):
    _inherit = "shopinvader_api_address.service.base_address"
    _name = "shopinvader_api_address.service.invoicing_address"
    _description = "Shopinvader Api Address Service Invoicing Address"
    _odoo_address_type = "invoice"

    @property
    def _odoo_model_domain_restrict(self):
        return [("id", "=", self.partner_id)]
