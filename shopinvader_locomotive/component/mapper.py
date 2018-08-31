# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.components.mapper import mapping, changed_by
import json


class LocomotiveExportMapper(AbstractComponent):
    _name = 'locomotive.export.mapper'
    _inherit = ['base.locomotive.connector', 'base.export.mapper']
    _usage = 'export.mapper'


class ShopinvaderSiteExportMapper(Component):
    _name = 'shopinvader.site.export.mapper'
    _inherit = ['locomotive.export.mapper']
    _apply_on = 'shopinvader.backend'

    @mapping
    @changed_by('allowed_country_ids')
    def country(self, record):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            for country in record.with_context(
                    lang=lang.code).allowed_country_ids:
                res[lang.code[0:2]].append({
                    'name': country.name,
                    'id': country.id,
                    })
        return {'available_countries': res}

    @mapping
    @changed_by('filter_ids')
    def filters(self, record):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            for pfilter in record.with_context(lang=lang.code).filter_ids:
                res[lang.code[0:2]].append({
                    'code': pfilter.display_name,
                    'name': pfilter.name,
                    'help': pfilter.help,
                    })
        return {'all_filters': res}

    def finalize(self, map_record, values):
        values = super(ShopinvaderSiteExportMapper, self).finalize(
            map_record, values)
        return {key: json.dumps(vals) for key, vals in values.items()}
