# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector_locomotivecms.unit.binder import LocomotiveBinder
from openerp.addons.connector_locomotivecms.backend import locomotive


@locomotive
class LocomotiveEcommerce(LocomotiveBinder):
    _model_name = [
        'locomotive.partner',
    ]
