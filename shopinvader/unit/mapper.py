# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.connector_generic.unit.mapper import GenericExportMapper

import logging

_logger = logging.getLogger(__name__)


@locomotive
class PartnerExportMapper(GenericExportMapper):
    _model_name = 'locomotive.partner'

    direct = [
        ('email', 'email'),
        ('name', 'name'),
    ]
