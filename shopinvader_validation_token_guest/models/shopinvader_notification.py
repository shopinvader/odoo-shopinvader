# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    def _get_security_token_notification(self):
        """
        Get security token notifications.
        :return: dict
        """
        values = super(
            ShopinvaderNotification, self
        )._get_security_token_notification()

        values.update(
            {
                "partner_token_guest": {
                    "name": _("Security token Guest"),
                    "model": "shopinvader.security.token",
                },
            }
        )
        return values
