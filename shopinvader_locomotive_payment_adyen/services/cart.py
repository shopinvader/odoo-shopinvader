# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

# Locomotive proxy do not implement any logic, it's 100% generic it's just
# pass the data its receive, we need here to map the field and to inject
# header information into params


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _add_params_from_header(self, params):
        params.update(
            {
                "accept_header": self.client_header["ACCEPT"],
                "user_agent": self.client_header["USER_AGENT"],
                "shopper_ip": self.client_header["IP"],
            }
        )

    def _process_payment_provider(self, provider_name, cart, params):
        if provider_name == "adyen":
            self._add_params_from_header(params)
        return super(CartService, self)._process_payment_provider(
            provider_name, cart, params
        )

    def check_payment(self, provider_name=None, **params):
        if provider_name == "adyen":
            self._add_params_from_header(params)
            params["md"] = params.pop("MD")
            params["pares"] = params.pop("PaRes")
        return super(CartService, self).check_payment(
            provider_name=provider_name, **params
        )
