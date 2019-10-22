# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    @property
    def partner_user(self):
        # partner that matches the real user on client side.
        # The standard `self.partner` will match `partner_user`
        # only when the main customer account is logged in.
        # When a user logs in w/ a sub-user for a company
        # `partner` will be the company and `partner_user`
        # will be its contact account logged in on client side.
        return self.work.partner_user
