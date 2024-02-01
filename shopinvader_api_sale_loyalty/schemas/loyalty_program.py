# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class LoyaltyProgram(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_loyalty_program(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
        )
