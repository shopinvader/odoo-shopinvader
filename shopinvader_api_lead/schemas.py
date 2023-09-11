from pydantic import BaseModel


class LeadService(BaseModel):
    email: str | None = None
    name: str | None = None
    description: str | None = None
    company: str | None = None
    street: str | None = None
    street2: str | None = None
    zip: str | None = None
    city: str | None = None
    phone: str | None = None
    mobile: str | None = None
    state_id: int | None = None
    country_id: int | None = None
    team_id: int | None = None
    contact_name: str | None = None

    # # faire un module supp pour ces champs
    # if "crm_lead_firstname" in odoo_env().registry._init_modules:
    #     contact_firstname: str
    #     # contact_name: str = pydantic.Field(alias="contact_firstname") | None
    #     contact_lastname: str
    # else:
    #     contact_name: str

    def to_crm_lead_vals(self, partner=None) -> dict:
        vals = {
            "email_from": self.email,
            "name": self.name,
            "description": self.description,
            "partner_name": self.company,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "phone": self.phone,
            "mobile": self.mobile,
            "state_id": self.state_id,
            "country_id": self.country_id,
            "team_id": self.team_id,
            "contact_name": self.contact_name,
        }
        if partner:
            vals.pop("email_from", None)
            vals["partner_id"] = partner.id
        return vals
