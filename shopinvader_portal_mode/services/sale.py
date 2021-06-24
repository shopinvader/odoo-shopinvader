# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.osv import expression

from odoo.addons.component.core import Component


class SaleService(Component):
    _inherit = "shopinvader.sale.service"
    _usage = "sales"

    def _get_base_search_domain(self):
        portal_mode = self.shopinvader_backend.sale_order_portal_mode
        if not portal_mode:
            return super()._get_base_search_domain()
        domain = self._default_domain_for_partner_records(
            with_backend=False
        ) + [("state", "in", self._portal_mode_sale_states())]
        backend_domain = [
            "|",
            ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
            ("shopinvader_backend_id", "=", False),
        ]
        domain = expression.AND([domain, backend_domain])
        return expression.normalize_domain(domain)

    def _portal_mode_sale_states(self):
        return ("sale", "done")

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res["from_shop"] = bool(sale.shopinvader_backend_id)
        return res
