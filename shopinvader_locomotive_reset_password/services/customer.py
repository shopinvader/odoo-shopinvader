# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.component.core import Component


class Customer(Component):
    _inherit = "shopinvader.customer.service"

    def _assign_cart_and_get_store_cache(self):
        res = super(Customer, self)._assign_cart_and_get_store_cache()
        shop_partner = self.env["shopinvader.partner"].search(
            [
                ("backend_id", "=", self.shopinvader_backend.id),
                ("record_id", "=", self.partner.id),
            ]
        )
        if not shop_partner.last_pwd_reset_datetime:
            shop_partner.last_pwd_reset_datetime = datetime.now()
        return res
