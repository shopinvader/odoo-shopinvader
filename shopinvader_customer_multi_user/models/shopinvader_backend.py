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
            # Field name or dotted path to a res.partner relation
            # suitable for `shopinvader.partner.mapped`
            ("main_partner_id", "Main partner"),
            ("record_id", "User's partner"),
        ],
        default="main_partner_id",
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
    multi_user_records_policy = fields.Selection(
        selection=[
            # Field name or dotted path to a res.partner relation
            # suitable for `shopinvader.partner.mapped`
            ("main_partner_id", "View main partner records"),
            ("parent_id", "View parent partner records"),
            ("record_id", "View current partner records only"),
        ],
        default="main_partner_id",
        help="This affects the behavior of every endpoint "
        "which lists partner related records, directy or indirectly.\n"
        "\n`View main partner records`: "
        "view all records coming from main partner and its children. "
        "Usually this is the main company of the user."
        "\n`View parent partner records`: "
        "view all records coming from parent partner and its children. "
        "Usually this is the main company but it can be any sub partner "
        "such as a contact or delivery address or invoice address. "
        "\n`View current partner records only`: "
        "view only records related to current partner. ",
    )
    multi_user_main_partner_domain = fields.Char(
        default="[]",
        help="This affects the behavior of `main_partner_id` computation "
        "when no specific value is passed.\n"
        "The computation is done by walking up in the hierarchy of partners "
        "to get the the uppermost partner.\n"
        "Here you can set - for instance - only delivery partners "
        "are considered main partners.\n"
        "The parent record will be always checked against this domain.\n"
        "NOTE: if you change this value existing records won't be affected "
        "as the field is stored to allow manual customization.",
    )
