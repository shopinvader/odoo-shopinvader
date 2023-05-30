# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from odoo import models
from odoo.fields import first

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping

_logger = logging.getLogger(__name__)


class ShopinvaderSiteExportMapper(Component):
    _name = "shopinvader.site.export.mapper"
    _inherit = ["locomotive.export.mapper"]
    _apply_on = "shopinvader.backend"

    def _m2m_to_external(self, record, backend_field, parser):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = []
            # Make sure no value is cached in the former lang processed
            # TODO: tested manually and it works. Needs test coverage.
            record.invalidate_cache([backend_field])
            field_value = record[backend_field]
            if isinstance(field_value, models.Model):
                field_value.invalidate_cache()
            for rec in field_value.with_context(lang=lang.code):
                res[lang.code[0:2]].append(rec.jsonify(parser, one=True))
        return res

    @mapping
    @changed_by("allowed_country_ids")
    def country(self, record):
        return {
            "available_countries": self._m2m_to_external(
                record,
                "allowed_country_ids",
                ["id", "name", ("state_ids:states", ["code", "name"])],
            )
        }

    @mapping
    @changed_by("visible_filter_ids")
    def filters(self, record):
        return {
            "all_filters": self._m2m_to_external(
                record,
                "visible_filter_ids",
                ["name", "display_name:code", "help"],
            )
        }

    @mapping
    @changed_by("currency_ids")
    def currencies_rate(self, record):
        res = {}
        for currency in record.currency_ids:
            res[currency.name.upper()] = currency.rate
        return {"currencies_rate": res}

    @mapping
    @changed_by("lang_ids")
    def locale_mapping(self, record):
        res = {}
        for lang in record.lang_ids:
            res[lang.code[0:2]] = lang.code
        return {"locale_mapping": res}

    @mapping
    def erp_config(self, record):
        erp = self.options["current_values"].get("erp", {})
        if self.options["force"] or not erp.get("api_key"):
            erp["api_key"] = record.auth_api_key_id.key
        if self.options["force"] or not erp.get("api_url"):
            erp["api_url"] = "{}/shopinvader".format(
                record.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
        return {"erp": erp}

    @mapping
    def search_engine_config(self, record):
        se_backend = record.se_backend_id
        if not se_backend:
            _logger.warning("No search engine configured yet.")
            return {}
        if not se_backend.search_engine_name:
            _logger.warning("No search engine name declared.")
            return {}
        return {se_backend.search_engine_name: self._search_engine_config(se_backend)}

    def _search_engine_config(self, se_backend):
        config = self.options["current_values"].get(se_backend.search_engine_name, {})
        if self.options["force"] or not config.get("indices"):
            indices, routes = self._get_indexes_config(se_backend)
            config["indices"] = json.dumps(indices)
            config["routes"] = json.dumps(routes)
        # TODO: we could improve this.
        # The best would be to use a specific mapper
        # applied only on the specific backend model
        # and use this mapper from the site mapper.
        specific_handler = getattr(
            self,
            "_{}_config".format(se_backend.search_engine_name),
            lambda se_backend, config: config,
        )
        return specific_handler(se_backend, config)

    def _get_indexes_config(self, se_backend):
        # we've 2 models exported. product.category and product.product.
        # we must export for each model, the name 'without the code lang'
        # of the index to use for the model and the route
        indices = []
        routes = []
        index_categ = first(
            se_backend.index_ids.filtered(
                lambda i: i.model_id.model == "shopinvader.category"
            )
        )
        if index_categ:
            indices.append(
                {
                    "name": "categories",
                    "index": self._get_index_name(index_categ),
                }
            )
            routes.append(
                [
                    "*",
                    {
                        "name": "category",
                        "template_handle": "category",
                        "index": "categories",
                    },
                ]
            )
        index_product = first(
            se_backend.index_ids.filtered(
                lambda i: i.model_id.model == "shopinvader.variant"
            )
        )
        if index_product:
            indices.append(
                {
                    "name": "products",
                    "index": self._get_index_name(index_product),
                }
            )
            routes.append(
                [
                    "*",
                    {
                        "name": "product",
                        "template_handle": "product",
                        "index": "products",
                    },
                ]
            )
        return indices, routes

    def _get_index_name(self, index):
        return index.name.replace("_{}".format(index.lang_id.code), "")

    @mapping
    @changed_by("partner_title_ids")
    def partner_titles(self, record):
        return {
            "available_customer_titles": self._m2m_to_external(
                record, "partner_title_ids", ["id", "name", "shortcut"]
            )
        }

    @mapping
    @changed_by("partner_industry_ids")
    def partner_industries(self, record):
        return {
            "available_customer_industries": self._m2m_to_external(
                record, "partner_industry_ids", ["id", "name", "full_name"]
            )
        }

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
        values = super().finalize(map_record, values)
        current_values = self.options["current_values"]
        store_values = current_values.setdefault("_store", {})
        for key, vals in values.items():
            if key in current_values:
                current_values[key].update(vals)
            else:
                store_values.update({key: json.dumps(vals)})
        return current_values
