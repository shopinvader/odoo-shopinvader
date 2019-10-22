# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    customer_multi_user = fields.Boolean(
        default=False,  # let's be explicit here :)
        help="Turn on this flag to enable multiple users per each partner. "
        "Customers will be able to register as many users as they want "
        "by providing their company token. "
        "Every order and every notification "
        "will be associated to the main partner. "
        "Simple users can manage their own address "
        "and use it for invoicing or shipping. "
        "Addresses must be validated before frontend users can use them.",
    )
