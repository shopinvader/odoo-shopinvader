# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited,method-required-super

from odoo.addons.component.core import Component


class DeliveryCarrierService(Component):
    _inherit = "shopinvader.delivery.carrier.service"

    def _validator_search(self):
        schema = super(DeliveryCarrierService, self)._validator_search()
        schema["cart_uuid"] = {
            "type": "string",
            "required": False,
            "nullable": False,
        }
        return schema

    # Services implementation

    def _search(self, **params):
        """
        Search for delivery carriers
        :param params: see _validator_search
        :return: delivery.carriers recordset
        """
        cart_uuid = params.get("cart_uuid")
        if cart_uuid:
            cart = self._get_cart_from_uuid(cart_uuid)
            country = self._load_country(params)
            zip_code = self._load_zip_code(params)
            if country or zip_code:
                cart = cart.with_context(
                    delivery_force_country_id=country.id,
                    delivery_force_zip_code=zip_code,
                )
            return cart.shopinvader_available_carrier_ids
        return super(DeliveryCarrierService, self)._search(**params)

    def _get_cart_from_uuid(self, uuid):
        # TO BE REFACTORED
        v2_cart_service = self.work.components_registry.lookup(
            "shopinvader.api.v2",
            usage="cart",
        )[0](self.work)
        # the collection and the service is not properly initialized
        # but just want to get the cart
        return v2_cart_service._find_open_cart(uuid)
