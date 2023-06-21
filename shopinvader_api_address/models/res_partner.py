# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError

from ..schemas import AddressInput, AddressSearch,AddressUpdate


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _billing_address_already_used(self):
        self.ensure_one()
        move_id = self.env["account.move"].search([("commercial_partner_id","=",self.id)],limit=1)
        return len(move_id)>0

    @api.model
    def _create_vals_shopinvader_address(self, data: AddressInput,authenticated_partner_id:"ResPartner",type:str) -> dict:
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
            "parent_id": authenticated_partner_id.id,
            "type": type,
        }
        return vals
    
    @api.model
    def _update_vals_shopinvader_address(self, data: AddressUpdate) -> dict:
        vals={}
        if data.name is not None:
            vals["name"] = data.name
        if data.street is not None:
            vals["street"] = data.street
        if data.street2 is not None:
            vals["street2"] = data.street2
        if data.zip is not None:
            vals["zip"] = data.zip
        if data.city is not None:
            vals["city"] = data.city
        if data.phone is not None:
            vals["phone"] = data.phone
        if data.email is not None:
            vals["email"] = data.email

        # search on state/country is performed
        # on name or code of state/country
        #TODO country/state

        return vals

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

    #### Billing ####
    # Billing address is unique and corresponds to authenticated_partner
    

    @api.model
    def _get_shopinvader_billing_address(self, authenticated_partner_id: "ResPartner") -> "ResPartner":
        return authenticated_partner_id
    
    @api.model
    def _update_shopinvader_billing_address(self, authenticated_partner_id: "ResPartner",data: AddressUpdate) -> "ResPartner":
        vals = self._update_vals_shopinvader_address(data)

        #if billing address is already used, it is not possible to modify it
        if authenticated_partner_id._billing_address_already_used():
            raise UserError(_("Can not update billing address because it is already used on billings"))
        
        authenticated_partner_id.write(vals)

        return authenticated_partner_id
    

    #### Shipping ####

    @api.model
    def _get_shopinvader_shipping_address(self,rec_id:int=None,data: AddressSearch=None) -> "ResPartner":
        if data is not None:
            data.type="delivery"
            domain = self._build_shopinvader_search_address_domain(data)
        else:
            domain = self._build_shopinvader_search_address_domain(AddressSearch(type="delivery"))
        
        if rec_id is not None:
            domain.append(("id", "=", rec_id))

        return self.env["res.partner"].search(domain)

    @api.model
    def _create_shipping_address(self,authenticated_partner_id: "ResPartner",data: AddressInput) -> "ResPartner":
        vals = self._create_vals_shopinvader_address(data,authenticated_partner_id,"delivery")
        return self.env["res.partner"].create(vals)

    def _update_shipping_address(self,data: AddressUpdate,rec_id:int) -> "ResPartner":
        address = self._get_shopinvader_shipping_address(rec_id)
        if not address:
            raise MissingError(_("No address found"))
        #update_address
        vals = self._update_vals_shopinvader_address(data)
        address.write(vals)
        return address
            

    @api.model
    def _delete_shipping_address(self,rec_id:int)-> None:
        address = self._get_shopinvader_shipping_address(rec_id)
        if address:
            #archive address
            address.active = False
