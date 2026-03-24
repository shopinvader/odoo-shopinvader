from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_router_helper import VirtualModel
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

address_router = APIRouter(tags=["addresses"])

AddressType = Literal["invoicing", "delivery"]

# TODO: Retrieve and centralize model functions inside the address helper


class AddressHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_address.address_router.helper"
    _description = "ShopInvader API Address Router Helper"
    _model = "res.partner"

    partner = fields.Many2one(
        comodel_name="res.partner",
    )

    def _domain(self):
        return []

    def _get_address(self, address_id: int, address_type: AddressType):
        partner = self.env["res.partner"]
        if address_type == "invoicing":
            partner = self.partner._get_shopinvader_invoicing_address(address_id)
        elif address_type == "delivery":
            partner = self.partner._get_shopinvader_delivery_address(address_id)

        return self.get(partner.id)

    def _search_addresses(self, address_type: AddressType):
        partners = self.env["res.partner"]
        if address_type == "invoicing":
            partners = self.partner._get_shopinvader_invoicing_addresses()
        elif address_type == "delivery":
            partners = self.partner._get_shopinvader_delivery_addresses()

        return self.search([("id", "in", partners.ids)])

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
        address.check_access("write")
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


def address_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_address.address_router.helper"].new(
        {"partner": partner}
    )


# --- Invoicing addresses ---


@address_router.get("/addresses/invoicing", response_model=list[InvoicingAddress])
def get_invoicing_addresses(
    helper: Annotated[AddressHelper, Depends(address_helper)],
) -> list[InvoicingAddress]:
    """
    Get invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    addresses = helper._search_addresses("invoicing")
    return [InvoicingAddress.from_res_partner(rec) for rec in addresses]


@address_router.get(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
def get_invoicing_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    address_id: int,
) -> InvoicingAddress:
    """
    Get invoicing address of authenticated user with specific address_id
    invoicing address corresponds to authenticated partner
    """
    address = helper._get_address(address_id, "invoicing")
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing", response_model=InvoicingAddress, status_code=201
)
def create_invoicing_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    data: InvoicingAddressCreate,
) -> InvoicingAddress:
    """
    Create invoicing address
    Raise error since invoicing address is the authenticated partner
    """
    address = helper._create_address(data, "invoicing")
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
def update_invoicing_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    data: InvoicingAddressUpdate,
    address_id: int,
) -> InvoicingAddress:
    """
    Update invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    address = helper._update_address(data, "invoicing", address_id)
    return InvoicingAddress.from_res_partner(address)


# --- Delivery address ---


@address_router.get("/addresses/delivery", response_model=list[DeliveryAddress])
def get_delivery_addresses(
    helper: Annotated[AddressHelper, Depends(address_helper)],
) -> list[DeliveryAddress]:
    """
    Get delivery addresses of authenticated user
    Can be used to get every delivery address: /addresses/delivery
    """
    addresses = helper._search_addresses("delivery")
    return [DeliveryAddress.from_res_partner(rec) for rec in addresses]


@address_router.get("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def get_delivery_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    address_id: int,
) -> DeliveryAddress:
    """
    Get delivery addresses of authenticated user
    Can be used to get one specific address: /addresses/delivery/address_id
    """
    address = helper._get_address(address_id, "delivery")
    return DeliveryAddress.from_res_partner(address)


@address_router.post(
    "/addresses/delivery", response_model=DeliveryAddress, status_code=201
)
def create_delivery_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    data: DeliveryAddressCreate,
) -> DeliveryAddress:
    """
    Create delivery address of authenticated user
    """
    address = helper._create_address(data, "delivery")
    return DeliveryAddress.from_res_partner(address)


@address_router.post("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def update_delivery_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    data: DeliveryAddressUpdate,
    address_id: int,
) -> DeliveryAddress:
    """
    Update delivery address of authenticated user
    """
    address = helper._update_address(data, "delivery", address_id)
    return DeliveryAddress.from_res_partner(address)


@address_router.delete("/addresses/delivery/{address_id}")
def delete_delivery_address(
    helper: Annotated[AddressHelper, Depends(address_helper)],
    address_id: int,
) -> None:
    """
    Delete delivery address of authenticated user
    Address will be archived.
    """
    helper._delete_address(address_id, "delivery")
