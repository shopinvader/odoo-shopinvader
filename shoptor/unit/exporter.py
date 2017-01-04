# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotivecms
from openerp.addons.connector_locomotivecms.unit.exporter import (
    LocomotivecmsExporter)

@locomotivecms
class ProductExporter(LocomotivecmsExporter):
    _model_name = 'locomotivecms.product'
