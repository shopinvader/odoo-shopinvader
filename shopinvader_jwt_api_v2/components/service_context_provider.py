# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component


class ShopinvaderAuthJwtServiceContextProvider(Component):
    _inherit = "auth_jwt.shopinvader.service.context.provider"
    _name = "auth_jwt.shopinvader.api.v2.service.context.provider"
    _collection = "shopinvader.api.v2"
