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

    def _get_all_schema(self):
        return {
            "countries": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_countries_schema(),
                },
            },
            "titles": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_titles_schema(),
                },
            },
            "industries": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_industries_schema(),
                },
            },
            "currencies": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_currencies_schema(),
                },
            },
            "languages": {
                "type": "list",
                "required": True,
                "nullable": False,
                "schema": {
                    "type": "dict",
                    "schema": self._get_languages_schema(),
                },
            },
        }

    @restapi.method(
        [(["/", "/all"], "GET")],
        output_param=restapi.CerberusValidator("_get_all_schema"),
        auth="public_or_default",
    )
    def get_all(self):
        return self._get_all()

    def _get_all(self):
        return {
            "countries": self._get_countries(),
            "titles": self._get_titles(),
            "industries": self._get_industries(),
            "currencies": self._get_currencies(),
            "languages": self._get_languages(),
        }

    def _jsonify_fields_country(self):
        return [
            "name",
            "code",
            "id",
        ]

    def _get_countries(self):
        return self.shopinvader_backend.allowed_country_ids.jsonify(
            self._jsonify_fields_country()
        )

    def _get_countries_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "code": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
        }

    @restapi.method(
        [(["/countries"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_get_countries_schema", unique_items=True
        ),
        auth="public_or_default",
    )
    def countries(self):
        return self._get_countries()

    def _jsonify_fields_title(self):
        return [
            "id",
            "name",
        ]

    def _get_titles(self):
        return self.shopinvader_backend.partner_title_ids.jsonify(
            self._jsonify_fields_title()
        )

    def _get_titles_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
        }

    @restapi.method(
        [(["/titles"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_get_titles_schema", unique_items=True
        ),
        auth="public_or_default",
    )
    def titles(self):
        return self._get_titles()

    def _jsonify_fields_industry(self):
        return [
            "id",
            "name",
        ]

    def _get_industries(self):
        return self.shopinvader_backend.partner_industry_ids.jsonify(
            self._jsonify_fields_industry()
        )

    def _get_industries_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
        }

    @restapi.method(
        [(["/industries"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_get_industries_schema", unique_items=True
        ),
        auth="public_or_default",
    )
    def industries(self):
        return self._get_industries()

    def _jsonify_fields_currency(self):
        return [
            "id",
            "name",
        ]

    def _get_currencies(self):
        return self.shopinvader_backend.currency_ids.jsonify(
            self._jsonify_fields_currency()
        )

    def _get_currencies_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
        }

    @restapi.method(
        [(["/currencies"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_get_currencies_schema", unique_items=True
        ),
        auth="public_or_default",
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
        return self.shopinvader_backend.lang_ids.jsonify(self._jsonify_fields_lang())

    def _get_languages_schema(self):
        return {
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
            },
            "iso_code": {
                "type": "string",
                "required": True,
                "nullable": False,
            },
        }

    @restapi.method(
        [(["/languages"], "GET")],
        output_param=restapi.CerberusListValidator(
            "_get_languages_schema", unique_items=True
        ),
        auth="public_or_default",
    )
    def languages(self):
        return self._get_languages()
