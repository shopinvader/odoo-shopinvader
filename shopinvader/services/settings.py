# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class ExportSettingsService(Component):
    """Shopinvader service to expose allowed settings"""

    _inherit = [
        "base.shopinvader.service",
    ]
    _name = "shopinvader.settings.service"
    _usage = "settings"
    _description = __doc__

    @restapi.method(
        [(["/", "/get"], "GET")],
        auth="public",
    )
    def get(self):
        return {
            **self._get_countries(),
            **self._get_titles(),
            **self._get_industries(),
            **self._get_currencies(),
            **self._get_languages(),
        }

    def _jsonify_fields_country(self):
        return [
            "name",
            "code",
            "id",
        ]

    def _get_countries(self):
        countries = self.shopinvader_backend.allowed_country_ids.jsonify(
            self._jsonify_fields_country()
        )
        return {"countries": countries}

    @restapi.method(
        [(["/countries"], "GET")],
        auth="public",
    )
    def countries(self):
        return self._get_countries()

    def _jsonify_fields_title(self):
        return [
            "id",
            "name",
        ]

    def _get_titles(self):
        titles = self.shopinvader_backend.partner_title_ids.jsonify(
            self._jsonify_fields_title()
        )
        return {"titles": titles}

    @restapi.method(
        [(["/titles"], "GET")],
        auth="public",
    )
    def titles(self):
        return self._get_titles()

    def _jsonify_fields_industry(self):
        return [
            "id",
            "name",
        ]

    def _get_industries(self):
        industries = self.shopinvader_backend.partner_industry_ids.jsonify(
            self._jsonify_fields_industry()
        )
        return {"industries": industries}

    @restapi.method(
        [(["/industries"], "GET")],
        auth="public",
    )
    def industries(self):
        return self._get_industries()

    def _jsonify_fields_currency(self):
        return [
            "id",
            "name",
        ]

    def _get_currencies(self):
        currencies = self.shopinvader_backend.currency_ids.jsonify(
            self._jsonify_fields_currency()
        )
        return {"currencies": currencies}

    @restapi.method(
        [(["/currencies"], "GET")],
        auth="public",
    )
    def currencies(self):
        return self._get_currencies()

    def _jsonify_fields_lang(self):
        return [
            "id",
            "name",
            "iso_code",
        ]

    def _get_languages(self):
        languages = self.shopinvader_backend.lang_ids.jsonify(
            self._jsonify_fields_lang()
        )
        return {"languages": languages}

    @restapi.method(
        [(["/languages"], "GET")],
        auth="public",
    )
    def languages(self):
        return self._get_languages()
