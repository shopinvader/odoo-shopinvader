# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class ClientExportMapper(AbstractComponent):
    _name = "shopinvader.client.export.mapper"
    _inherit = ["shopinvader.client.connector", "base.export.mapper"]
    _usage = "export.mapper"


class ShopinvaderSiteExportMapper(Component):
    _name = "shopinvader.site.export.mapper"
    _inherit = ["shopinvader.client.export.mapper"]
    _apply_on = "shopinvader.backend"

    @mapping
    @changed_by("allowed_country_ids", "lang_ids")
    def country(self, record):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            for country in record.with_context(
                lang=lang.code
            ).allowed_country_ids:
                res[lang.code[0:2]].append(
                    {"name": country.name, "id": country.id}
                )
        return {"available_countries": res}

    @mapping
    @changed_by("filter_ids", "lang_ids")
    def filters(self, record):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            for pfilter in record.with_context(lang=lang.code).filter_ids:
                res[lang.code[0:2]].append(
                    {
                        "code": pfilter.display_name,
                        "name": pfilter.name,
                        "help": pfilter.help,
                    }
                )
        return {"all_filters": res}

    @mapping
    @changed_by("currency_ids")
    def currencies_rate(self, record):
        res = {}
        for currency in record.currency_ids:
            res[currency.name.upper()] = currency.rate
        return {"currencies_rate": res}

    # def finalize(self, map_record, values):
    #     values = super().finalize(map_record, values)
    #     # TODO: is this really need or just for Locomotive?
    #     return {key: json.dumps(vals) for key, vals in values.items()}
