# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class QuotationService(Component):
    _inherit = "shopinvader.quotation.service"

    def _get_base_search_domain(self):
        if not self.shopinvader_backend.sale_order_portal_mode:
            return super()._get_base_search_domain()
        domain = self._default_domain_for_partner_records(with_backend=False)
        domain += [("typology", "=", "quotation")]
        domain += [("state", "in", self._portal_mode_sale_states())]
        domain += [
            "|",
            ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
            ("shopinvader_backend_id", "=", False),
        ]
        return domain

    def _portal_mode_sale_states(self):
        return ("sent",)

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res["from_shop"] = bool(sale.shopinvader_backend_id)
        return res

    def _confirm(self, order):
        # If user can see all quotations, bind the order to current backend if not set yet.
        if self.shopinvader_backend.sale_order_portal_mode:
            if not order.shopinvader_backend_id:
                order.shopinvader_backend_id = self.shopinvader_backend
        return super()._confirm(order)
