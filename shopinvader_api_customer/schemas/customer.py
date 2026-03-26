# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class Customer(StrictExtendableBaseModel):
    """
    used to get customer details
    """

    email: str
    name: str | None = None
    phone: str | None = None
    mobile: str | None = None
    opt_in: bool | None = False
    pricelist_id: int | None = None
    lang_id: int | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        env = odoo_rec.env
        return cls.model_construct(
            email=odoo_rec.email or None,
            name=odoo_rec.name or None,
            phone=odoo_rec.phone or None,
            mobile=odoo_rec.mobile or None,
            opt_in=not odoo_rec.is_blacklisted,
            pricelist_id=odoo_rec.property_product_pricelist.id,
            lang_id=env["res.lang"]._lang_get(odoo_rec.lang).id,
        )


class CustomerUpdate(StrictExtendableBaseModel, extra="ignore"):
    """
    used to update customer details
    """

    name: str | None = None
    phone: str | None = None
    mobile: str | None = None
    opt_in: bool | None = None
    lang_id: int | None = None

    def to_res_partner_vals(self) -> dict:
        fields = self._get_partner_update_fields()
        values = self.model_dump(exclude_unset=True)
        values = {f: values[f] for f in fields if f in values}
        return values

    def _get_partner_update_fields(self):
        return [
            "name",
            "phone",
            "mobile",
        ]
