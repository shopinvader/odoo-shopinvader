# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class AddressCreate(BaseModel, metaclass=ExtendableModelMeta):
    """
    used to create new address (res.partner)
    state and country can be name or code
    """

    name: Optional[str]
    street: Optional[str]
    street2: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]

    def to_res_partner_vals(self) -> dict:
        vals = {
            "name": self.name,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "phone": self.phone,
            "email": self.email,
            "state_id": self.state_id,
            "country_id": self.country_id,
        }

        return vals


class AddressUpdate(BaseModel, metaclass=ExtendableModelMeta):
    """
    used to update address (res.partner)
    state and country can be name or code
    """

    name: Optional[str]
    street: Optional[str]
    street2: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    state_id: Optional[int]
    country_id: Optional[int]

    def to_res_partner_vals(self) -> dict:
        vals = {
            "name": self.name,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "phone": self.phone,
            "email": self.email,
            "state_id": self.state_id,
            "country_id": self.country_id,
        }

        return vals


# --- Billing Address ---
class BillingAddressCreate(AddressUpdate):
    """
    Creation of Billing Address

    Remark: it is actually not used since
    the billing address is the authenticated
    partner's address
    """

    vat: Optional[str]

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["vat"] = self.vat

        return vals


class BillingAddressUpdate(AddressUpdate):
    """
    Update of Billing Address
    """

    vat: Optional[str]

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["vat"] = self.vat

        return vals


# --- Shipping Address ---


class ShippingAddressCreate(AddressUpdate):
    """
    Creation of Shipping Address
    """


class ShippingAddressUpdate(AddressUpdate):
    """
    Update of Shipping Address
    """
