# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError

from ..schemas import AddressInput,AddressUpdate


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _billing_address_already_used(self):
        self.ensure_one()
        move_id = self.env["account.move"].sudo().search([("commercial_partner_id","=",self.id)],limit=1)
        return len(move_id)>0

    @api.model
    def _create_vals_shopinvader_address(self, data: AddressInput,authenticated_partner_id:"ResPartner",type:str) -> dict:
        vals = self.env["shopinvader_api_address.mapper"]._addressInput_to_res_partner(data)
        vals.update({
            "parent_id": authenticated_partner_id.id,
            "type": type or "",
        })
        return vals
    
    @api.model
    def _update_vals_shopinvader_address(self, data: AddressUpdate) -> dict:
        vals = self.env["shopinvader_api_address.mapper"]._addressupdate_to_res_partner(data)
        return vals

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
    def _get_shopinvader_shipping_address(self,authenticated_partner_id: "ResPartner",rec_id:int=None) -> "ResPartner":
        domain = [("type","=","delivery")]
        
        if rec_id is not None:
            domain.append(("id", "=", rec_id))

        addresses = self.env["res.partner"].search(domain)

        #TODO
        #include main address
        # addresses += authenticated_partner_id

        return addresses

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
        #TODO check it is not main address
        if address:
            #archive address
            address.active = False
