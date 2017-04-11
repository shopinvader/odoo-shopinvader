# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.connector_locomotivecms.unit.deleter import (
    LocomotiveDeleter)


@locomotive
class ProductDeleter(LocomotiveDeleter):
    _model_name = 'locomotive.product'


@locomotive
class PartnerDeleter(LocomotiveDeleter):
    _model_name = 'locomotive.partner'


@locomotive
class CategoryDeleter(LocomotiveDeleter):
    _model_name = 'locomotive.category'
