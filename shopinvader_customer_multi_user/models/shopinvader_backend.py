# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
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
    multi_user_profile_policy = fields.Selection(
        selection=[
            ("main_partner", "Main partner"),
            ("user_partner", "User's partner"),
        ],
        default="main_partner",
        help="This affects the behavior of the /customer endpoint "
        "as well as the behavior of any service acting on the current partner.\n"
        "\n`Main partner`: the main profile for the shop frontend "
        "will be the main partner (usually the company). "
        "\nThis means:\n"
        "* orders will be assigned to the main account\n"
        "* in the profile form you'll see the main account data "
        "but you'll be able to edit only if permissions allow to.\n"
        "\n`User's partner`: the main profile for the shop frontend "
        "will be the partner of the current user. "
        "\nThis means:\n"
        "* orders will be assigned to the specific partner\n"
        "* in the profile form you'll see the your own account data "
        "and you'll be able to edit\n"
        "* profile info will include a reference to the main account "
        "inside the `main_account` key.",
    )
