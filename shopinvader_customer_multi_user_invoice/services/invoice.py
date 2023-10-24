# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class InvoiceService(Component):
    _inherit = "shopinvader.invoice.service"

    def _get_invoice_domain(self):
        """
        Overwrite method to fit custom needs, self.partner is always Main partner id
        TODO: Adjust for multi_user options
        """
        return [
            ("partner_id", "child_of", self.partner.id),
            ("type", "in", ["out_invoice", "out_refund"]),
        ]
