# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class ExportSettingsService(Component):
    _inherit = [
        "shopinvader.settings.service",
    ]

    def _get_all_schema(self):
        schema = super()._get_all_schema()
        schema.update(**self._get_es_settings_schema())
        return schema

    def _get_all(self):
        res = super()._get_all()
        res.update(**self._get_es_settings())
        return res

    def _get_es_settings_schema(self):
        return {
            "elasticsearch": {
                "required": True,
                "nullable": True,
                "type": "dict",
                "schema": {
                    "host": {
                        "type": "string",
                        "required": True,
                        "nullable": False,
                    },
                    "indexes": {
                        "meta": {
                            "description": "A key/value mapping where Key is the "
                            "model name used to fill the index "
                            "and value is the index name",
                            "example": {
                                "shopinvader.category": "demo_elasticsearch_backend"
                                "_shopinvader_category_en_US",
                                "shopinvader.variant": "demo_elasticsearch_backend"
                                "_shopinvader_variant_en_US",
                            },
                        },
                        "type": "dict",
                        "required": True,
                        "nullable": True,
                        "keysrules": {"type": "string"},
                        "valuesrules": {
                            "type": "string",
                            "required": True,
                            "nullable": False,
                        },
                    },
                },
            }
        }

    @restapi.method(
        [(["/elasticsearch"], "GET")],
        output_param=restapi.CerberusValidator("_get_es_settings_schema"),
        auth="public_or_default",
    )
    def get_es_settings(self):
        return self._get_es_settings()

    def _get_es_settings(self):
        se_backend = self.shopinvader_backend.se_backend_id
        settings = None
        if se_backend.search_engine_name == "elasticsearch":
            es_se_backend = se_backend.specific_backend
            indexes = {}
            for se_index in se_backend.index_ids.filtered(
                lambda idx: idx.lang_id.code == idx.env.context.get("lang")
            ):
                indexes[se_index.model_id.model] = se_index.name
            settings = {
                "host": es_se_backend.es_server_host,
                "indexes": indexes if indexes else None,
            }
        return {"elasticsearch": settings}
