# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_generic.unit.mapper import GenericExportMapper
from odoo.addons.connector.unit.mapper import mapping
from ..backend import shopinvader


@shopinvader
class ShopinvaderPartnerExportMapper(GenericExportMapper):
    _model_name = 'shopinvader.partner'

    direct = [
        ('email', 'email'),
    ]

    @mapping
    def role(self, record):
        return {'role': record.role_id.code}
