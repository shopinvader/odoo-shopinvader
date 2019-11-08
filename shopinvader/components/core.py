# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderComponent(AbstractComponent):
    """Base Shopinvader Component.

    All components of this module and inheriting ones should inherit from it.
    """

    _name = "base.shopinvader.component"
    _collection = "shopinvader.backend"

    @property
    def backend(self):
        return self.collection
