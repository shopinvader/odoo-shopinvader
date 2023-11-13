# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from . import LoyaltyProgram


class LoyaltyCard(StrictExtendableBaseModel):
    id: int
    program: LoyaltyProgram

    @classmethod
    def from_loyalty_card(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            program=LoyaltyProgram.from_loyalty_program(odoo_rec.program_id),
        )


class LoyaltyCardInput(StrictExtendableBaseModel):
    code: str
    reward_id: int | None = None
    free_product_id: int | None = None
