# Copyright 2025 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pydantic import BaseModel

from odoo.addons.shopinvader_schema_sale.schemas import Sale as BaseSale


class Substate(BaseModel):
    id: int
    name: str
    sequence: int
    description: str | None = None
    target_state: str | None = None
    target_state_name: str | None = None

    @classmethod
    def from_base_substate(cls, odoo_rec):
        return cls(
            id=odoo_rec.id,
            name=odoo_rec.name,
            sequence=odoo_rec.sequence,
            description=odoo_rec.description or None,
            target_state=odoo_rec.target_state_value_id.target_state_value,
            target_state_name=odoo_rec.target_state_value_id.name,
        )


class Sale(BaseSale, extends=True):
    current_substate: Substate | None = None
    available_substates: list[Substate] = []

    @classmethod
    def from_sale_order(cls, odoo_rec):
        obj = super().from_sale_order(odoo_rec)
        # Get current substate
        obj.current_substate = (
            Substate.from_base_substate(odoo_rec.substate_id)
            if odoo_rec.substate_id
            else None
        )
        # Get all substates for this model
        substate_type = odoo_rec._get_substate_type()
        domain = [
            ("target_state_value_id.base_substate_type_id", "=", substate_type.id),
            ("active", "=", True),
        ]
        available_substates = odoo_rec.env["base.substate"].search(domain)
        obj.available_substates = [
            Substate.from_base_substate(substate) for substate in available_substates
        ]
        return obj
