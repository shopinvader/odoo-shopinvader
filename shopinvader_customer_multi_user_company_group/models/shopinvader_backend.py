# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    multi_user_company_group_records_policy = fields.Selection(
        selection=[
            ("hierarchy", "View records down the company group hierarchy"),
            ("shared", "Share records across companies in the group"),
        ],
        help=(
            "This affects the behavior of every endpoint which lists partner related "
            "records, directy or indirectly.\n\n"
            "* `View records down the company group hierarchy`: Users that are part of "
            "the company group will see records from the companies that belong to it, "
            "but those companies users will only see their own company records.\n"
            "* `Share records across companies in the group`: Records will be shared "
            "among companies belonging to the same company group.\n"
        ),
        default="hierarchy",
        required=True,
    )
