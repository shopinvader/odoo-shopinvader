# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    validate_customers = fields.Boolean(
        default=False,  # let's be explicit here :)
        help="Turn on this flag to block non validated customers. "
        "If customers' partners are not validated, "
        "registered users cannot log in. "
        "Salesman will get notified via mail activity.",
    )
    validate_customers_type = fields.Selection(
        selection=[
            ("all", "Companies, simple users and addresses"),
            ("company", "Company users only"),
            ("user", "Simple users only"),
            ("company_and_user", "Companies and simple users"),
            ("address", "Addresses only"),
        ],
        default="all",
    )

    def _validate_partner(self, partner):
        """Hook to validate partners when required."""
        with self.work_on(partner._name) as work:
            validator = work.component(usage="partner.validator")
            validator.validate_partner(partner)
