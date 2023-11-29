# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.shopinvader_schema_sale.schemas import delivery

from ..schemas import DeliveryCarrier, Picking


class DeliveryAmount(StrictExtendableBaseModel):
    tax: float
    untaxed: float
    total: float

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            tax=odoo_rec.shipping_amount_tax,
            untaxed=odoo_rec.shipping_amount_untaxed,
            total=odoo_rec.shipping_amount_total,
        )


class DeliveryInfo(delivery.DeliveryInfo, extends=True):
    amount: DeliveryAmount | None = None
    selected_carrier: DeliveryCarrier | None = None
    pickings: list[Picking] = []

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.amount = DeliveryAmount.from_sale_order(odoo_rec)
        res.selected_carrier = (
            DeliveryCarrier.from_delivery_carrier(odoo_rec.carrier_id)
            if odoo_rec.carrier_id
            else None
        )
        res.pickings = [
            Picking.from_picking(picking)
            for picking in odoo_rec.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "outgoing"
            )
        ]
        return res
