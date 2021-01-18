# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShopinvaderSecurityToken(models.Model):
    _inherit = "shopinvader.security.token"

    @api.model
    def _service_notification_map(self):
        """

        :return: dict
        """
        values = super(
            ShopinvaderSecurityToken, self
        )._service_notification_map()
        values.update({"shopinvader.guest.service": "partner_token_guest"})
        return values
