# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class UnitMember(StrictExtendableBaseModel):
    id: int
    name: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    state_id: int | None = None
    country_id: int | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or None,
            street=odoo_rec.street or None,
            street2=odoo_rec.street2 or None,
            zip=odoo_rec.zip or None,
            city=odoo_rec.city or None,
            phone=odoo_rec.phone or None,
            email=odoo_rec.email or None,
            state_id=odoo_rec.state_id.id or None,
            country_id=odoo_rec.country_id.id or None,
        )


class UnitMemberCreate(StrictExtendableBaseModel, extra="ignore"):
    type: str | None = "collaborator"
    name: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    state_id: int | None = None
    country_id: int | None = None

    def to_res_partner_vals(self) -> dict:
        vals = {
            "unit_profile": self.type,
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


class UnitMemberUpdate(StrictExtendableBaseModel, extra="ignore"):
    name: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
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
            "email",
            "state_id",
            "country_id",
        ]
        values = self.model_dump(exclude_unset=True)
        return {f: values[f] for f in fields if f in values}
