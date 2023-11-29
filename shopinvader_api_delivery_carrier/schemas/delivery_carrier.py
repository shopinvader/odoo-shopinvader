# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class DeliveryCarrierInput(StrictExtendableBaseModel):
    carrier_id: int


class DeliveryCarrierSearch(StrictExtendableBaseModel):
    country_id: int | None = None
    zipcode: str | None = None


class DeliveryCarrier(StrictExtendableBaseModel):
    id: int
    name: str
    code: str | None = None
    description: str | None = None

    @classmethod
    def from_delivery_carrier(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            code=odoo_rec.code or None,
            description=odoo_rec.carrier_description or None,
        )


class DeliveryCarrierWithPrice(DeliveryCarrier):
    price_applied_to_cart: float | None = None

    @classmethod
    def from_delivery_carrier(cls, odoo_rec, cart=None):
        """
        If a cart is passed, add into price_applied_to_cart
        the specific price of this delivery carrier applied to the cart.
        """
        res = super().from_delivery_carrier(odoo_rec)
        price_applied_to_cart = None
        if cart:
            price_applied_to_cart = odoo_rec.rate_shipment(cart).get("price", 0.0)
        res.price_applied_to_cart = price_applied_to_cart
        return res
