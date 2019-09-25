# coding: utf-8
# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping
from odoo.addons.server_environment import serv_config


class ShopinvaderSiteExportMapper(Component):
    _name = "shopinvader.site.export.mapper"
    _inherit = ["locomotive.export.mapper"]
    _apply_on = "shopinvader.backend"

    @mapping
    @changed_by("allowed_country_ids")
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
    @changed_by("filter_ids")
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

    @mapping
    def erp_config(self, record):
        api_key = None
        section_name = record.auth_api_key_name
        for section in serv_config.sections():
            if section == section_name and serv_config.has_option(
                section, "key"
            ):
                api_key = serv_config.get(section, "key")
        erp = self.options["current_values"].get("erp", {})
        if self.options["force"] or not erp.get("api_key"):
            erp["api_key"] = api_key
        if self.options["force"] or not erp.get("api_url"):
            erp["api_url"] = (
                record.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url")
            )
        return {"erp": erp}

    def finalize(self, map_record, values):
        """
           By default, custom information are stored in the field "_store"
           of the site. Initially, it was not possible to update any other
           information from the site. To remove this limitation, without
           breaking existing code, the following euristic has been put in
           place.
           If the key of a value provided by the mapper is a key
           of the current mmetafields values from the site, we update this
           key into the metafields.
           Otherwise, this key is a custom field part of the '_store'
           sub-dictionary and the its value must be serialized
       """
        values = super(ShopinvaderSiteExportMapper, self).finalize(
            map_record, values
        )
        current_values = self.options["current_values"]
        store_values = current_values.setdefault("_store", {})
        for key, vals in values.items():
            if key in current_values:
                current_values[key].update(vals)
            else:
                store_values.update({key: json.dumps(vals)})
        return current_values
