# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE Sa/ (http://www.acsone.eu)
# Cédric Pigeon <cedric.pigeon@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.controllers import main
from odoo.http import route


class InvaderController(main.InvaderController):
    @route(["/shopinvader/cart/get_delivery_methods"], methods=["GET"])
    def get_delivery_methods(self, **params):
        # deprecated!!!
        return self._process_method("cart", "get_delivery_methods", params)
