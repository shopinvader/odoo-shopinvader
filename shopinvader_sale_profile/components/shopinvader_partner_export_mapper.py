# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _inherit = "shopinvader.partner.export.mapper"

    @mapping
    def role(self, record):
        if not record.backend_id.use_sale_profile:
            return super(ShopinvaderPartnerExportMapper, self).role(record)
        return {"role": record.sale_profile_id.code}
