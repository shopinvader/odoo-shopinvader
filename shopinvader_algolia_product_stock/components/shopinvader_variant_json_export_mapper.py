# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopinvaderVariantJsonExportMapper(Component):
    """
    Apply the export mapper to the Algolia search engine backend
    """
    _inherit = 'shopinvader.variant.json.export.mapper'
    _collection = 'se.backend.algolia'
