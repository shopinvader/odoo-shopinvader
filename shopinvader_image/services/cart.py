# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo.addons.component.core import Component


_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def _build_common_response_schema(self):
        """
        Inherit to add:
        data/lines/items/product/images
        :return: list
        """
        items = super(CartService, self)._build_common_response_schema()
        image_schema = {
            # No more details on the dict keys/values
            'type': 'dict',
        }
        items.extend([
            ('images', 'data/lines/items/product', image_schema),
        ])
        return items

    @property
    def _search_response_schema(self):
        return self._common_response_schema()
