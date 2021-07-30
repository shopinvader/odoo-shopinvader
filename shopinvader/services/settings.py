# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class ExportSettingsService(Component):
    """Shopinvader service to export allowed settings"""

    _inherit = [
        "base.shopinvader.service",
    ]
    _name = "shopinvader.export.settings.service"
    _usage = "settings"
    _description = __doc__

    def get(self):
        return {
            **self._get_country(),
            **self._get_title(),
            **self._get_industry(),
            **self._get_currency(),
            **self._get_lang(),
        }

    def _jsonify_fields_country(self):
        return [
            "name",
            "code",
            "id",
        ]

    def _get_country(self):
        countries = self.shopinvader_backend.allowed_country_ids.jsonify(
            self._jsonify_fields_country()
        )
        return {"countries": countries}

    @restapi.method(
        [(["/country/get"], "GET")],
        auth="api_key",
    )
    def get_country(self):
        return self._get_country()

    def _jsonify_fields_title(self):
        return [
            "id",
            "name",
        ]

    def _get_title(self):
        titles = self.shopinvader_backend.partner_title_ids.jsonify(
            self._jsonify_fields_title()
        )
        return {"titles": titles}

    @restapi.method(
        [(["/title/get"], "GET")],
    )
    def get_title(self):
        return self._get_title()

    def _jsonify_fields_industry(self):
        return [
            "id",
            "name",
        ]

    def _get_industry(self):
        industries = self.shopinvader_backend.partner_industry_ids.jsonify(
            self._jsonify_fields_industry()
        )
        return {"industries": industries}

    @restapi.method(
        [(["/industry/get"], "GET")],
    )
    def get_industry(self):
        return self._get_industry()

    def _jsonify_fields_currency(self):
        return [
            "id",
            "name",
        ]

    def _get_currency(self):
        currencies = self.shopinvader_backend.currency_ids.jsonify(
            self._jsonify_fields_currency()
        )
        return {"currencies": currencies}

    @restapi.method(
        [(["/currency/get"], "GET")],
    )
    def get_currency(self):
        return self._get_currency()

    def _jsonify_fields_lang(self):
        return [
            "id",
            "name",
            "iso_code",
        ]

    def _get_lang(self):
        languages = self.shopinvader_backend.lang_ids.jsonify(
            self._jsonify_fields_lang()
        )
        return {"languages": languages}

    @restapi.method(
        [(["/lang/get"], "GET")],
    )
    def get_lang(self):
        return self._get_lang()
