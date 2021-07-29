# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderConfigSettings(models.TransientModel):

    _inherit = "shopinvader.config.settings"

    group_allow_customer_pwd_edit = fields.Boolean(
        string="Allow customer password edit",
        implied_group="shopinvader_locomotive_password_mgmt.group_manage_customer_pwd",
    )
