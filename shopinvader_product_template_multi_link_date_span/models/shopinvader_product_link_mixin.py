# Copyright 2021 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderProductLinkMixin(models.AbstractModel):
    _inherit = "shopinvader.product.link.mixin"

    def _get_product_link_data(self, link):
        res = super()._get_product_link_data(link)
        if link.type_id.limited_by_dates:
            res.update(
                {
                    "date_start": fields.Date.to_string(link.date_start),
                    "date_end": fields.Date.to_string(link.date_end),
                }
            )
        return res
