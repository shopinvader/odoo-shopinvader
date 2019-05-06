# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopinvaderSiteExportMapper(Component):
    _inherit = "shopinvader.site.export.mapper"

    direct = [("is_guest_mode_allowed", "is_guest_mode_allowed")]
