from typing import Annotated, List, Literal

from fastapi import APIRouter, Depends

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_schema_address.schemas import (
    DeliveryAddress,
    InvoicingAddress,
)

from ..schemas import (
    DeliveryAddressCreate,
    DeliveryAddressUpdate,
    InvoicingAddressCreate,
    InvoicingAddressUpdate,
)

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Invoicing addresses ---


@address_router.get("/addresses/invoicing", response_model=List[InvoicingAddress])
def get_invoicing_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[InvoicingAddress]:
    """
    Get invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_invoicing_addresses()
    return [InvoicingAddress.from_res_partner(rec) for rec in address]


@address_router.get(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
def get_invoicing_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> InvoicingAddress:
    """
    Get invoicing address of authenticated user with specific address_id
    invoicing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_invoicing_address(address_id)
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing", response_model=InvoicingAddress, status_code=201
)
def create_invoicing_address(
    data: InvoicingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> InvoicingAddress:
    """
    Create invoicing address
    Raise error since invoicing address is the authenticated partner
    """
    helper = env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )
    address = helper._create_address(data, "invoicing")
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
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
    helper = env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )
    address = helper._update_address(data, "invoicing", address_id)
    return InvoicingAddress.from_res_partner(address)


# --- Delivery address ---


@address_router.get("/addresses/delivery", response_model=List[DeliveryAddress])
def get_delivery_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[DeliveryAddress]:
    """
    Get delivery addresses of authenticated user
    Can be used to get every delivery address: /addresses/delivery
    """
    addresses = partner._get_shopinvader_delivery_addresses()
    return [DeliveryAddress.from_res_partner(rec) for rec in addresses]


@address_router.get("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def get_delivery_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Get delivery addresses of authenticated user
    Can be used to get one specific address: /addresses/delivery/address_id
    """
    addresses = partner._get_shopinvader_delivery_address(address_id)
    return DeliveryAddress.from_res_partner(addresses)


@address_router.post(
    "/addresses/delivery", response_model=DeliveryAddress, status_code=201
)
def create_delivery_address(
    data: DeliveryAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> DeliveryAddress:
    """
    Create delivery address of authenticated user
    """
    helper = env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )
    address = helper._create_address(data, "delivery")
    return DeliveryAddress.from_res_partner(address)


@address_router.post("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def update_delivery_address(
    data: DeliveryAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Update delivery address of authenticated user
    """
    helper = env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )
    address = helper._update_address(data, "delivery", address_id)
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
    helper = env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )
    helper._delete_address(address_id, "delivery")


AddressType = Literal["invoicing", "delivery"]


class ShopinvaderApiAddressRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_address.address_router.helper"
    _description = "ShopInvader API Address Router Helper"

    partner = fields.Many2one(
        comodel_name="res.partner",
    )

    def _get_address(self, address_id: int, address_type: AddressType):
        self.ensure_one()
        return getattr(self.partner, f"_get_shopinvader_{address_type}_address")(
            address_id
        )

    def _prepare_create_address_vals(
        self,
        data: InvoicingAddressCreate | DeliveryAddressCreate,
        address_type: AddressType,
    ):
        return data.to_res_partner_vals()

    def _prepare_update_address_vals(
        self,
        data: InvoicingAddressUpdate | DeliveryAddressUpdate,
        address_type: AddressType,
        address: ResPartner,
    ):
        return data.to_res_partner_vals()

    def _create_address(
        self,
        data: InvoicingAddressCreate | DeliveryAddressCreate,
        address_type: AddressType,
    ):
        vals = self._prepare_create_address_vals(data, address_type)
        if address_type == "invoicing":
            return self.partner._create_shopinvader_invoicing_address(vals)
        elif address_type == "delivery":
            return self.partner._create_shopinvader_delivery_address(vals)
        else:
            raise ValueError(f"Unknown address type: {address_type}")

    def _update_address(
        self,
        data: InvoicingAddressUpdate | DeliveryAddressUpdate,
        address_type: AddressType,
        address_id: int,
    ):
        address = self._get_address(address_id, address_type)
        vals = self._prepare_update_address_vals(data, address_type, address)
        # sudo() is needed because some addons override the write
        # function of res.partner to do some checks before writing.
        # These checks need more rights than what we are giving to
        # the enspoint's user
        # (e.g. snailmail/models/res_partner.py)
        partner_sudo = self.partner.sudo()
        address.check_access_rights("write")
        address.check_access_rule("write")
        address_sudo = address.sudo()
        updated_address = False
        if address_type == "invoicing":
            updated_address = partner_sudo._update_shopinvader_invoicing_address(
                vals, address_sudo
            )
        elif address_type == "delivery":
            updated_address = partner_sudo._update_shopinvader_delivery_address(
                vals, address_sudo
            )
        else:
            raise ValueError(f"Unknown address type: {address_type}")
        return updated_address.sudo(False)

    def _delete_address(
        self,
        address_id: int,
        address_type: AddressType,
    ):
        address = self._get_address(address_id, address_type)
        # sudo() is needed because some addons override the write
        # function of res.partner to do some checks before writing.
        # These checks need more rights than what we are giving to
        # the enspoint's user
        # (e.g. snailmail/models/res_partner.py)
        partner_sudo = self.partner.sudo()
        if address_type == "invoicing":
            partner_sudo._delete_shopinvader_invoicing_address(address)
        elif address_type == "delivery":
            partner_sudo._delete_shopinvader_delivery_address(address)
        else:
            raise ValueError(f"Unknown address type: {address_type}")
