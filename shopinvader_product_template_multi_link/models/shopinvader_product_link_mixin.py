# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models

from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.addons.http_routing.models.ir_http import slugify


class ShopinvaderProductLinkMixin(models.AbstractModel):
    _name = "shopinvader.product.link.mixin"
    _description = "Shopinvader product link mixin"

    product_links = Serialized(
        string="Product template links", compute="_compute_product_links"
    )

    def _compute_product_links(self):
        for record in self:
            record.product_links = record._get_product_links_by_type(
                record._get_product_links().filtered(lambda x: x.is_link_active)
            )

    def _get_product_links(self):
        return self.product_template_link_ids

    def _get_product_links_by_type(self, links):
        """Retrieve variants as list of ids by link type.

        Eg: {"up_selling": [{id: 1}, {id: 2}, {id: 3}]}

        :return: dict
        """
        self.ensure_one()
        grouped = defaultdict(self.env["product.template.link"].browse)
        for link in links.sorted(lambda x: x.id):
            code = self._product_link_code(link)
            grouped[code] |= link
        res = defaultdict(list)
        for code, links in grouped.items():
            for link in links:
                data = self._get_product_link_data(link)
                if data:
                    res[code].append(data)
        return res

    def _product_link_code(self, link):
        """Normalize link code, default to `generic` when missing."""
        return slugify(link.type_id.code or "generic").replace("-", "_")

    def _get_product_link_data(self, link):
        target = self._product_link_target(link)
        if not target:
            return {}
        variant = self._product_link_target_variant(target)
        if variant:
            return {"id": variant.record_id.id}
        return {}

    def _product_link_target(self, link):
        """Retrieve the target of the link."""
        raise NotImplementedError()

    def _product_link_target_variant(self, target):
        """Retrieve variant ids for given target product

        :return: set
        """
        raise NotImplementedError()
