# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopinvaderVariantJsonStockExportMapper(Component):
    _inherit = 'shopinvader.variant.json.export.mapper'

    def _get_json_stock(self, shopinvader_variant):
        """
        Get the stock field value as a dict/json
        :param shopinvader_variant: shopinvader.variant
        :return: dict/json
        """
        values = {}
        backend = self.backend_record
        if backend.product_stock_field_id and backend.export_stock_key:
            stock_key = backend.export_stock_key
            values.update({
                stock_key: shopinvader_variant._get_se_backend_stock_value(),
            })
        return values

    def _apply(self, map_record, options=None):
        """
        Inherit the function to have json_akeneo values + shopinvader.variant
        values into one dict/json
        :param map_record: shopinvader.variant
        :param options: dict
        :return: dict/json
        """
        values = super(ShopinvaderVariantJsonStockExportMapper, self)._apply(
            map_record=map_record, options=options)
        values.update(self._get_json_stock(map_record.source))
        return values
