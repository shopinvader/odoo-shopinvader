# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    # FIXME: this could be avoided if we had `update` endpoint on `customer`.
    # See https://github.com/shopinvader/odoo-shopinvader/issues/530
    def _store_cache_needed(self, partner):
        needed = super()._store_cache_needed(partner)
        backend = self.shopinvader_backend
        shop_partner = partner.get_shop_partner(backend)
        # if the shop partner is the same as the profile one
        # then we want to cache it.
        return needed or shop_partner == partner
