# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions

from odoo.addons.component.core import Component


class ShopinvaderCustomerService(Component):
    _inherit = "shopinvader.customer.service"

    # Public methods

    def security_code_enabled(self, **params):
        """
        :param params: json/dict
        :return: dict/json
        """
        email = params.get("email")
        values = {"ask_security_code": False}
        EmailToken = self.env["shopinvader.security.token"]
        if EmailToken._should_trigger_security_token(
            backend=self.shopinvader_backend,
            email=email,
            service_name=self._name,
        ):
            values.update({"ask_security_code": True})
            if params.get("trigger_notification", True):
                security_token = EmailToken._generate_token(
                    self.shopinvader_backend, email, self._name
                )
                security_token._trigger_token_notification()
                values.update({"notification_sent": True})
        return values

    def validate_token(self, **params):
        """
        This service ensure the token is valid but doesn't consume it.
        """
        params = params or {}
        params.update({"consume": False})
        self._ensure_token_valid(params)
        return {}

    def _ensure_token_valid(self, params):
        """
        Get the token form given params (and remove it).
        Then continue process (yield)
        Finally ensure the token was valid.
        Execute this validity check after the yield to let the process create
        the partner if necessary
        :param params: dict/json
        :return:
        """
        email = params.get("email")
        token = params.pop("token", "")
        consume = params.pop("consume", True)
        EmailToken = self.env["shopinvader.security.token"]
        if EmailToken._should_trigger_security_token(
            backend=self.shopinvader_backend,
            email=email,
            service_name=self._name,
        ):
            if not EmailToken._check_token_is_valid(
                email, token, self.shopinvader_backend, self._name, consume=consume
            ):
                raise exceptions.UserError(_("Invalid/Expired token"))
        return True

    def create(self, **params):
        self._ensure_token_valid(params)
        return super().create(**params)

    # Validators

    def _validator_security_code_enabled(self):
        schema = {
            "email": {"type": "string", "required": True},
            "trigger_notification": {"type": "boolean", "required": False},
        }
        return schema

    def _validator_return_security_code_enabled(self):
        schema = {
            "ask_security_code": {"type": "boolean", "required": True},
            "notification_sent": {"type": "boolean", "required": False},
        }
        return schema

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update({"token": {"type": "string", "required": False}})
        return schema

    def _validator_validate_token(self):
        schema = {
            "email": {"type": "string", "required": True},
            "token": {"type": "string", "required": True},
        }
        return schema

    def _validator_return_validate_token(self):
        schema = {}
        return schema
