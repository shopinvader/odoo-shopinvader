# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.connector_locomotivecms.unit.adapter import (
    LocomotiveContentAdapter,
    LocomotiveAssetAdapter)


@locomotive
class ProductAdapter(LocomotiveContentAdapter):
    _model_name = 'locomotive.product'
    _content_type = 'products'


@locomotive
class CategAdapter(LocomotiveContentAdapter):
    _model_name = 'locomotive.category'
    _content_type = 'categories'


@locomotive
class PartnerAdapter(LocomotiveContentAdapter):
    _model_name = 'locomotive.partner'
    _content_type = 'customers'


@locomotive
class AssetAdapter(LocomotiveAssetAdapter):
    _model_name = [
        'locomotive.image',
        'locomotive.media',
        ]
