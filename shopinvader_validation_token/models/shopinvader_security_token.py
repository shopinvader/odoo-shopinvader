# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import _lang_get


class ShopinvaderSecurityToken(models.Model):
    _name = "shopinvader.security.token"
    _description = "Shopinvader security token"

    email = fields.Char(
        required=True,
    )
    expiration_datetime = fields.Datetime(
        string="Token's expiration",
        required=True,
        readonly=True,
    )
    token = fields.Char(
        required=True,
        index=True,
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
        help="Become inactive when the token is used.",
    )
    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        required=True,
    )
    notification_type = fields.Char(required=True)
    lang = fields.Selection(
        _lang_get,
        string="Language",
        default=lambda self: self.env.lang,
    )

    _sql_constraints = [
        ("uniq_token", "unique(token)", "This token already exists!"),
    ]

    def _consume(self):
        """

        :return: bool
        """
        return self.sudo().write({"active": False})

    @api.model
    def _disable_expired_token(self):
        """
        Disable every expired or un-used token.
        Should be used in a cron.
        :return:
        """
        now = fields.Datetime.now()
        domain = [
            "|",
            ("active", "=", False),
            ("expiration_datetime", "<", now),
        ]
        shopinvader_tokens = self.sudo().search(domain)
        if shopinvader_tokens:
            shopinvader_tokens.unlink()

    @api.model
    def _service_notification_map(self):
        """

        :return: dict
        """
        return {
            "shopinvader.customer.service": "partner_token_customer",
        }

    @api.model
    def _should_trigger_security_token(self, backend, email, service_name):
        """
        Check if the notification partner_token_* is enabled
        on the related backend.
        As we have the backend, email and the service who do this check,
        we can precisely check if the token is required or not.
        :param backend: shopinvader.backend recordset
        :param email: str
        :param service_name: str
        :return: bool
        """
        # We have to force the backend when the current shopinvader.partner
        # doesn't exist yet.
        backend.ensure_one()
        should_trigger = False
        if service_name and backend:
            notif_type = self._service_notification_map().get(service_name, "")
            if notif_type:
                should_trigger = any(
                    n.notification_type == notif_type for n in backend.notification_ids
                )
        return should_trigger

    def _trigger_token_notification(self):
        """
        Generate the shopinvader.security.token and trigger the notification
        on it.
        :return:
        """
        self.ensure_one()
        self.shopinvader_backend_id._send_notification(self.notification_type, self)

    @api.model
    def _get_new_token(self, backend, email):
        """
        Generate a new token/code
        :param backend: shopinvader.backend recordset
        :param email: str
        :return: str
        """
        return "{:06d}".format(randint(0, 999999))

    @api.model
    def _generate_token(self, backend, email, service_name):
        """
        Generate the shopinvader.security.token
        Before generate a new token, check if the email is already linked to a not consumed
        token.
        If yes, increase the expiration_datetime and return it.
        If not, create the token and return it.
        :return: shopinvader.security.token
        """
        now = fields.Datetime.from_string(fields.Datetime.now())
        notif_type = self._service_notification_map().get(service_name)
        domain = [
            ("shopinvader_backend_id", "=", backend.id),
            ("email", "=", email),
            ("active", "=", True),
            ("expiration_datetime", ">", now),
            ("notification_type", "=", notif_type),
        ]
        expiration = now + relativedelta(minutes=backend.token_validity)
        expiration_datetime = fields.Datetime.to_string(expiration)
        shopinvader_token = self.search(domain, limit=1)
        if not shopinvader_token:
            token = self._get_new_token(backend, email)
            lang = self.env.context.get("lang") or "en_US"
            if lang not in backend.lang_ids.mapped("code"):
                lang = fields.first(backend.lang_ids).code
            values = {
                "shopinvader_backend_id": backend.id,
                "email": email,
                "token": token,
                "expiration_datetime": expiration_datetime,
                "notification_type": notif_type,
                "lang": lang,
            }
            shopinvader_token = self.create(values)
        else:
            shopinvader_token.write({"expiration_datetime": expiration_datetime})
        return shopinvader_token

    @api.model
    def _check_token_is_valid(self, email, token, backend, service_name, consume=True):
        """
        Check if the given token on the current shopinvader partner is valid
        :param email: str
        :param token: str
        :return: bool
        """
        valid = False
        if self._should_trigger_security_token(backend, email, service_name):
            date_fs = fields.Datetime.from_string
            date_ts = fields.Datetime.to_string
            notif_type = self._service_notification_map().get(service_name)
            now = date_fs(fields.Datetime.now())
            domain = [
                ("shopinvader_backend_id", "=", backend.id),
                ("email", "=", email),
                ("token", "=", token),
                ("notification_type", "=", notif_type),
                ("active", "=", True),
                ("expiration_datetime", ">=", date_ts(now)),
            ]
            shopinvader_token = self.search(domain, limit=1)
            if shopinvader_token:
                if consume:
                    shopinvader_token._consume()
                valid = True
        else:
            valid = True
        return valid
