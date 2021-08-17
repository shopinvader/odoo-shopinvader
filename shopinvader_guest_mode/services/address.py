# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.shopinvader import shopinvader_response


class AddressService(Component):

    _inherit = "shopinvader.address.service"

    def update(self, _id, **params):
        """
        As the base update() modifies the store_cache["customer"],
        we need to add email as it is used by locomotive with headers
        to set partner
        :param _id:
        :param params:
        :return:
        """
        address = self._get(_id)
        res = super().update(_id=_id, **params)
        guest = self.component(usage="guest")
        binding = guest._get_binding(address.email)
        if binding.is_guest and binding.address_type == "profile":
            response = shopinvader_response.get()
            store_cache = response.store_cache
            customer = store_cache["customer"]
            customer.update({"email": address.email})
            response.set_store_cache("customer", customer)
        return res
