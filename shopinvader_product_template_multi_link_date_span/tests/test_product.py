# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_product_template_multi_link.tests.common import (
    ProductLinkCaseBase,
)


class ProductLinkCase(ProductLinkCaseBase):
    def test_link_json_data(self):
        self.cross_selling_type.limited_by_dates = True
        links = self.shopinvader_variant_2_1.shopinvader_product_id.product_links

        for key, _links in links.items():
            if key == "cross_selling":
                for link in _links:
                    self.assertIn("date_start", link)
                    self.assertIn("date_end", link)
            else:
                for link in _links:
                    self.assertNotIn("date_start", link)
                    self.assertNotIn("date_end", link)
