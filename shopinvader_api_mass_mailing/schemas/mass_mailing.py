# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class SubscribeInput(StrictExtendableBaseModel):
    name: str | None = None
    email: str


class UnsubscribeInput(StrictExtendableBaseModel):
    email: str


class Subscription(StrictExtendableBaseModel):
    name: str | None = None
    email: str
    opt_out: bool = False

    @classmethod
    def from_mailing_contact(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name or None,
            email=odoo_rec.email,
            opt_out=odoo_rec.opt_out,
        )
