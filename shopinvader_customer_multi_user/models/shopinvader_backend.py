# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    customer_multi_user = fields.Boolean(
        default=False,  # let's be explicit here :)
        help="Turn on this flag to enable multiple users per each company. "
        "Customers will be able to register many users that will used "
        "the same data for shipping and invoicing.",
    )
