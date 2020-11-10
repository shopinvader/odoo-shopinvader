# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.component.core import Component


class InvoiceService(Component):
    _inherit = "shopinvader.invoice.service"

    def _get_sale_order_domain(self):
        return self._default_domain_for_partner_records() + [
            ("typology", "=", "sale")
        ]
