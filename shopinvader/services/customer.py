# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited,method-required-super

from odoo.addons.component.core import Component

from ..models.shopinvader_partner import STATE_ACTIVE, STATE_PENDING


class CustomerService(Component):
    """Shopinvader service to create and edit customers.
    """

    _inherit = [
        "base.shopinvader.service",
        "shopinvader.partner.service.mixin",
    ]
    _name = "shopinvader.customer.service"
    _usage = "customer"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.
    def get(self):
        if self.partner:
            customer = self._to_customer_info(self.partner)
            return {"data": customer, "store_cache": {"customer": customer}}
        else:
            return {"data": {}}

    # pylint: disable=W8106
    def create(self, **params):
        vals = self._prepare_params(params)
        binding = self.env["shopinvader.partner"].create(vals)
        self._load_partner_work_context(binding)
        self._post_create(self.work.partner)
        return self._prepare_create_response(binding)

    def sign_in(self, **params):
        return self._assign_cart_and_get_store_cache()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_sign_in(self):
        return {}

    def _validator_create(self):
        address = self.component(usage="addresses")
        schema = address._validator_create()
        exclude_keys = ["type"]
        for key in exclude_keys:
            schema.pop(key, None)
        schema.update(
            {
                "email": {"type": "string", "required": True},
                "external_id": {"type": "string", "required": True},
                "vat": {"type": "string", "required": False},
                "company_name": {"type": "string", "required": False},
                "function": {"type": "string", "required": False},
            }
        )
        return schema

    def _prepare_params(self, params, mode="create"):
        address = self.component(usage="addresses")
        params = address._prepare_params(params, mode=mode)
        pricelist = self.shopinvader_backend._get_customer_default_pricelist()
        # fmt: off
        params.update(
            {
                "backend_id": self.shopinvader_backend.id,
                "property_product_pricelist": pricelist.id if pricelist else None,
            }
        )
        # fmt: on
        if mode == "create":
            if params.get("is_company"):
                params["is_company"] = True
            enabled = self.partner_validator.enabled_by_params(
                params, "profile"
            )
            params["state"] = STATE_ACTIVE if enabled else STATE_PENDING
        return params

    def _get_and_assign_cart(self):
        cart_service = self.component(usage="cart")
        cart = cart_service._get(create_if_not_found=False)
        if cart:
            if self.partner and cart.partner_id != self.partner:
                # we need to affect the cart to the partner
                cart.write_with_onchange(
                    {
                        "partner_id": self.partner.id,
                        "partner_shipping_id": self.partner.id,
                        "partner_invoice_id": self.partner.id,
                    }
                )
            return cart_service._to_json(cart)["data"]
        else:
            return {}

    def _assign_cart_and_get_store_cache(self):
        cart = self._get_and_assign_cart()
        customer = self._to_customer_info(self.partner)
        result = {"store_cache": {"cart": cart, "customer": customer}}
        if cart:
            result["set_session"] = {"cart_id": cart["id"]}
        return result

    def _to_customer_info(self, partner):
        address = self.component(usage="addresses")
        info = address._to_json(partner)[0]
        # access info on the current record partner record
        info["access"] = self.access_info.for_profile(partner.id)
        # global permission for current partner user
        info["permissions"] = self.access_info.permissions()
        return info

    def _prepare_create_response(self, binding):
        response = self._assign_cart_and_get_store_cache()
        response["data"] = {
            "id": binding.record_id.id,
            "name": binding.name,
            "role": binding.role,
        }
        return response
