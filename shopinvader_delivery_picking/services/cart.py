# Copyright 2017 Akretion (http://www.akretion.com)
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    # Validator
    def _validator_update(self):
        res = super(CartService, self)._validator_update()
        res["picking_policy"] = {"type": "string", "nullable": False}
        res["commitment_date"] = {"type": "string", "nullable": True}
        return res
