# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderSiteExportMapper(Component):
    _inherit = ["shopinvader.site.export.mapper"]

    def _get_index_name(self, index):
        return index.name.replace("_{}".format(index.lang_id.code), "")

    @mapping
    def elasticsearch_config(self, record):
        config = self.options["current_values"].get("elasticsearch", {})
        se_backend_id = record.se_backend_id
        if self.options["force"] or not config.get("url"):
            config["url"] = se_backend_id.specific_backend.es_server_host
        if self.options["force"] or not config.get("indices"):
            # we've 2 models exported. product.category and product.product.
            # we must export for each model, the name 'without the code lang'
            # of the index to use for the model and the route
            indices = []
            routes = []
            index_categ = se_backend_id.index_ids.filtered(
                lambda i: i.model_id.model == "shopinvader.category"
            )
            if index_categ:
                index_categ = index_categ[0]
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
            index_product = se_backend_id.index_ids.filtered(
                lambda i: i.model_id.model == "shopinvader.variant"
            )
            if index_product:
                index_product = index_product[0]
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
            config["indices"] = json.dumps(indices)
            config["routes"] = json.dumps(routes)

        return {"elasticsearch": config}
