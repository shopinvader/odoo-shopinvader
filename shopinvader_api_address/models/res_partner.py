# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError

from ..schema import AddressInput, AddressSearch


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _create_vals_shopinvader_address(self, data: AddressInput) -> dict:
        state_id = self.env["res.country.state"].search(
            [
                "|",
                ("name", "=", data.state),
                ("code", "=", data.state),
            ],
            limit=1,
        )

        country_id = self.env["res.country"].search(
            [
                "|",
                ("name", "=", data.country),
                ("code", "=", data.country),
            ]
        )

        vals = {
            "name": data.name,
            "street": data.street,
            "street2": data.street2 or "",
            "zip": data.zip,
            "city": data.city,
            "phone": data.phone or "",
            "email": data.email or "",
            "state_id": state_id.id,
            "country_id": country_id.id,
            "parent_id": self.env.context.get("authenticated_partner_id"), #take authenticated partner from fastapi 
            "type": data.type,
        }
        return vals

    @api.model
    def _create_shopinvader_address(self, data: AddressInput) -> "ResPartner":
        vals = self._create_vals_shopinvader_address(data)
        return self.env["res.partner"].create(vals)

    @api.model
    def _get_shopinvader_address(self, rec_id: int) -> "ResPartner":
        address = self.env["res.partner"].search([("id", "=", rec_id)], limit=1)
        if not address:
            raise MissingError(_("No address found"))
        return address

    @api.model
    def _build_shopinvader_search_address_domain(self, query: AddressSearch) -> list:
        domain = []

        if query.name is not None:
            domain.append(("name", "ilike", query.name))
        if query.street is not None:
            domain.append(("street", "ilike", query.name))
        if query.street2 is not None:
            domain.append(("street2", "ilike", query.name))
        if query.zip is not None:
            domain.append(("zip", "ilike", query.name))
        if query.city is not None:
            domain.append(("city", "ilike", query.name))
        if query.phone is not None:
            domain.append(("phone", "ilike", query.name))
        if query.email is not None:
            domain.append(("email", "ilike", query.name))
        if query.type is not None:
            domain.append(("type", "=", query.type))

        # search on state/country is performed
        # on name or code of state/country
        if query.state is not None:
            domain += [
                "|",
                ("state_id.name", "ilike", query.state),
                ("state_id.code", "ilike", query.state),
            ]
        if query.country is not None:
            domain += [
                "|",
                ("country.name", "ilike", query.country),
                ("country.code", "ilike", query.country),
            ]

        return domain

    @api.model
    def _search_shopinvader_address(
        self, query: AddressSearch, limit, offset
    ) -> "ResPartner":
        domain = self._build_shopinvader_search_address_domain(query)
        return self.env["res.partner"].search(domain, limit=limit, offset=offset)

    @api.model
    def _delete_shopinvader_address(self, rec_id: int):
        address = self.env["res.partner"].search([("id", "=", rec_id)], limit=1)
        if not address:
            raise MissingError(_("No address found"))

        # Try to delete authenticated_partner
        if address.id == int(self.env.context.get("authenticated_partner_id")):
            raise UserError(_("Can not delete the partner account"))

        address.unlink()

    @api.model
    def _get_shopinvader_billing_address(self, authenticated_partner_id: "ResPartner") -> "ResPartner":
        return authenticated_partner_id
    

    @api.model
    def _get_shopinvader_shipping_address(self,rec_id:int=None) -> "ResPartner":
        domain = self._build_shopinvader_search_address_domain(AddressSearch(type="delivery"))
        
        if rec_id is not None:
            domain.append(("id", "=", rec_id))

        return self.env["res.partner"].search(domain)