# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from collections import defaultdict

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ShopinvaderPartnerExportMapper(Component):
    _inherit = "shopinvader.partner.export.mapper"

    @mapping
    def wishlist(self, record):
        """Generate information for partner wishlists.

        :return: a dict in the form:

            {
                "product_wishlists": {
                    # product id : wishlist ids
                    pid1: [1, 2, 3],
                    pid2: [1, 2, 3],
                    pid3: [1, 2, 3],
                }
                "wishlists": {
                    # wishlist id: wishlist info
                    wid1: {"name": "Wishlist 1", "id": wid1},
                    wid2: {"name": "Wishlist 2", "id": wid2},
                }
            }
        """
        wishlists = self._get_wishlists(record)
        all_lines = wishlists.mapped("set_line_ids")
        products = defaultdict(list)
        for line in all_lines:
            products[line.product_id.id].append(line.product_set_id.id)
        return {
            # Locomotive does not support nested structured data plain.
            # You must encode inner data explicitly.
            "wishlists": json.dumps(
                {
                    x["id"]: x
                    for x in wishlists.jsonify(self._wishlist_parser())
                }
            ),
            "product_wishlists": json.dumps(products),
        }

    def _wishlist_parser(self):
        return ["id", "name"]

    def _get_wishlists(self, record):
        return self.env["product.set"].search(self._wishlist_domain(record))

    def _wishlist_domain(self, record):
        return [
            ("partner_id", "=", record.record_id.id),
            ("shopinvader_backend_id", "=", record.backend_id.id),
        ]
