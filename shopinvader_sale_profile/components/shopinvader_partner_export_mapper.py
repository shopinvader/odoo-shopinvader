# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _inherit = 'shopinvader.partner.export.mapper'

    @mapping
    def sale_profile(self, record):
        return {'sale_profile': record.sale_profile_id.code}
