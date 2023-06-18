# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from ..schema.schema import AddressSearch 


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _build_shopinvader_address_domain(self,query):  
        domain = []

        if query.name is not None:
            domain.append(("name","ilike",query.name))
        if query.street is not None:
            domain.append(("street","ilike",query.name))
        if query.street2 is not None:
            domain.append(("street2","ilike",query.name))
        if query.zip is not None:
            domain.append(("zip","ilike",query.name))
        if query.city is not None:
            domain.append(("city","ilike",query.name))
        if query.phone is not None:
            domain.append(("phone","ilike",query.name))
        if query.email is not None:
            domain.append(("email","ilike",query.name))

        #search on state/country is performed 
        # on name or code of state/country
        if query.state is not None:
            domain.join([
                "|",
                ("state_id.name","ilike",query.state),
                ("state_id.code","ilike",query.state),
            ])
        if query.country is not None:
            domain.join([
                "|",
                ("country.name","ilike",query.country),
                ("country.code","ilike",query.country),
            ])
        
        return domain 

    @api.model
    def _search_shopinvader_address(self,query:AddressSearch,limit,offset):
        """
            search using query
        """
        domain = self._build_shopinvader_address_domain(query) 
        return self.env["res.partner"].search(domain,limit=limit, offset=offset)
    
    @api.model
    def _create_vals_shopinvader_addres(self,data):
        vals = {
            "name": data.name,
            "street": data.street,
            "street2": data.street2 or "",
            "zip": data.zip,
            "city": data.city,
            "phone": data.phone or "",
            "email": data.email or "",
            "state": data.state or "", # TODO ampping
            "country": data.country or "", #TODO mapping
        }
        return vals

    @api.model
    def _create_shopinvader_address(self,data):
        vals= self._create_vals_shopinvader_addres(data)
        #TODO add mapping
        return self.env["res.partner"].sudo().create(vals)
    
    def _update_shopinvader_address(self,data):
        vals= self._create_vals_shopinvader_addres(data)
        #TODO add mapping
        #TODO search record
        #use vals to update record
        #return updated record
        return self.env["res.partner"].sudo().create(vals)