# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class AddressCreate(StrictExtendableBaseModel, extra="ignore"):
    """
    used to create new address (res.partner)
    state and country can be name or code
    """

    name: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    state_id: int | None = None
    country_id: int | None = None

    def to_res_partner_vals(self) -> dict:
        vals = {
            "name": self.name,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "phone": self.phone,
            "mobile": self.mobile,
            "email": self.email,
            "state_id": self.state_id,
            "country_id": self.country_id,
        }

        return vals


class AddressUpdate(StrictExtendableBaseModel, extra="ignore"):
    """
    used to update address (res.partner)
    state and country can be name or code
    """

    name: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    state_id: int | None = None
    country_id: int | None = None

    def to_res_partner_vals(self) -> dict:
        fields = [
            "name",
            "street",
            "street2",
            "zip",
            "city",
            "phone",
            "mobile",
            "email",
            "state_id",
            "country_id",
        ]
        values = self.model_dump(exclude_unset=True)
        return {f: values[f] for f in fields if f in values}


# --- Invoicing Address ---
class InvoicingAddressCreate(AddressCreate):
    """
    Creation of Invoicing Address

    Remark: it is actually not used since
    the invoicing address is the authenticated
    partner's address
    """

    vat: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["vat"] = self.vat

        return vals


class InvoicingAddressUpdate(AddressUpdate):
    """
    Update of Invoicing Address
    """

    vat: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["vat"] = self.vat

        return vals


# --- Delivery Address ---


class DeliveryAddressCreate(AddressCreate):
    """
    Creation of Delivery Address
    """


class DeliveryAddressUpdate(AddressUpdate):
    """
    Update of Delivery Address
    """
