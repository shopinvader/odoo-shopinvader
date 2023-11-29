# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from ..schemas import DeliveryCarrier


class Picking(StrictExtendableBaseModel):
    delivery_id: int
    name: str
    tracking_reference: str | None = None
    delivery_date: datetime | None = Field(
        None, description="Date done or Scheduled Date"
    )
    carrier: DeliveryCarrier | None = None
    sale_id: int | None = None

    @classmethod
    def from_picking(cls, odoo_rec):
        delivery_date = None
        if odoo_rec.date_done:
            delivery_date = odoo_rec.date_done
        elif odoo_rec.scheduled_date:
            delivery_date = odoo_rec.scheduled_date
        return cls.model_construct(
            delivery_id=odoo_rec.id,
            name=odoo_rec.name,
            tracking_reference=odoo_rec.carrier_tracking_ref or None,
            delivery_date=delivery_date,
            carrier=DeliveryCarrier.from_delivery_carrier(odoo_rec.carrier_id)
            if odoo_rec.carrier_id
            else None,
            sale_id=odoo_rec.sale_id.id or None,
        )
