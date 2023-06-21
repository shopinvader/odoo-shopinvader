# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid

from odoo import _, fields, models
from odoo.exceptions import AccessError


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    impersonate_token = fields.Char(index=True)
    datetime_expire_impersonate_token = fields.Datetime()

    def _generate_impersonate_url(self):
        # force_apply_redirection will force locomotive to apply the redirection
        # key send into the response
        return (
            f"{self.backend_id.location}/invader/customer/impersonate?"
            f"token={self.impersonate_token}"
            f"&email={self.email}"
            "&force_apply_redirection=True"
        )

    def impersonate(self):
        self.ensure_one()
        if not self.env.user.has_group(
            "shopinvader_locomotive_impersonate.group_shopinvader_impersonate"
        ):
            raise AccessError(_("You are not allowed to impersonate customer"))
        self.impersonate_token = str(uuid.uuid4())
        self.datetime_expire_impersonate_token = fields.Datetime.add(
            fields.Datetime.now(), minutes=5
        )
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": self._generate_impersonate_url(),
        }

    def _get_from_token(self, email, token):
        now = fields.Datetime.now()
        partner = self.search(
            [
                ("impersonate_token", "=", token),
                ("email", "=", email),
                ("datetime_expire_impersonate_token", ">", now),
            ],
            limit=1,
        )
        partner.write(
            {
                "impersonate_token": None,
                "datetime_expire_impersonate_token": None,
            }
        )
        return partner
