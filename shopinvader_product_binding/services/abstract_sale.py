# Copyright 2023 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _get_product_information(self, line):
        variant = line.product_id._get_invader_variant(
            self.shopinvader_backend, self.env.context.get("lang")
        )
        if not variant:
            _logger.debug(
                "No variant found with ctx lang `%s`. "
                "Falling back to partner lang `%s",
                self.env.context.get("lang"),
                line.order_id.partner_id.lang,
            )
            # this likely should never happen if the request from client
            # is forwarded properly
            variant = line.product_id._get_invader_variant(
                self.shopinvader_backend, line.order_id.partner_id.lang
            )
        if variant:
            return self._convert_one_line_product(variant)
        else:
            return super()._get_product_information(line)

    def _convert_one_line_product(self, variant):
        return variant.get_shop_data()
