# Copyright 2018 ACSONE SA/NV
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shopinvader_no_partner_duplicate = fields.Boolean(
        string="No partner duplicate",
        config_parameter="shopinvader.no_partner_duplicate",
        help="If checked, when a binding is created for a backend, we first "
        "try to find a partner with the same email and if found we link "
        "the new binding to the first partner found. Otherwise we always "
        "create a new partner",
    )
