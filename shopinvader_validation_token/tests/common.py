# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo.addons.shopinvader_v1_base.tests.common import CommonCase


class CommonValidationToken(CommonCase):
    def _get_usage(self):
        return ""

    def _get_partner(self):
        return self.env["res.partner"].browse()

    def _get_notification_type(self):
        return ""

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.data = {
            "email": "new@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": self.env.ref("base.fr").id},
        }
        self.shopinvader_partner_data = {
            "email": "new@customer.example.com",
            "name": "other partner",
            "backend_id": self.backend.id,
        }
        with self.work_on_services(
            partner=self._get_partner(),
            shopinvader_session=self.shopinvader_session,
        ) as work:
            self.service = work.component(usage=self._get_usage())
        self.shopinvader_config = self.env["res.config.settings"]
        self.token_model = self.env.ref(
            "shopinvader_validation_token.model_shopinvader_security_token"
        )
        self.mail_template = self.env.ref(
            "shopinvader_validation_token.mail_template_security_token"
        )
        self.ShopPartner = self.env["shopinvader.partner"]
        self.ShopEmailToken = self.env["shopinvader.security.token"]
        self.notification_type = self._get_notification_type()

    def _enable_security_token(self):
        self.backend.write(
            {
                "notification_ids": [
                    (
                        0,
                        False,
                        {
                            "notification_type": self.notification_type,
                            "model_id": self.token_model.id,
                            "template_id": self.mail_template.id,
                        },
                    )
                ]
            }
        )

    def _disable_security_token(self):
        notification = self.backend.notification_ids.filtered(
            lambda n: n.notification_type == self.notification_type
        )
        if notification:
            notification.unlink()

    def _ensure_token_consumed(self, token):
        """

        :param token: str
        :return: bool
        """
        shopinvader_token = self.ShopEmailToken.with_context(active_test=False).search(
            [("token", "=", token)], limit=1
        )
        self.assertFalse(shopinvader_token.active)
        return True

    def _ensure_token_not_consumed(self, token):
        """

        :param token: str
        :return: bool
        """
        shopinvader_token = self.ShopEmailToken.search(
            [("token", "=", token), ("active", "=", True)], limit=1
        )
        self.assertTrue(shopinvader_token.active)
        return True

    @contextmanager
    def _patch_get_new_token(self, forced_token):
        def _get_new_token(self_line, backend, email):
            return forced_token

        self.ShopEmailToken._patch_method("_get_new_token", _get_new_token)
        yield
        self.ShopEmailToken._revert_method("_get_new_token")
