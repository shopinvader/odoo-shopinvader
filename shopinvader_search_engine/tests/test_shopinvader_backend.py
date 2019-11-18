# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderBackend(CommonCase):
    """
    Tests for shopinvader.backend
    """

    def _create_technical_user(self):
        """

        :return:
        """
        return self.env["res.users"].create(
            {"name": "Super awesome technical user", "login": str(uuid4())}
        )

    def test_use_technical_user_if_set(self):
        """
        Check if the _use_technical_user_if_set change the current user (sudo)
        correctly.
        :return:
        """
        # For this case, disable the user_tech_id. So it should take current
        # user.
        user = self.env.user
        self.env.user.company_id.write({"user_tech_id": False})
        self.assertEqual(
            user, self.backend._use_technical_user_if_set().env.user
        )
        # Now create a technical user and assign it on the company
        user = self._create_technical_user()
        self.env.user.company_id.write({"user_tech_id": user.id})
        self.assertEqual(
            user, self.backend._use_technical_user_if_set().env.user
        )
        # Try with another technical user
        user = self._create_technical_user()
        self.env.user.company_id.write({"user_tech_id": user.id})
        self.assertEqual(
            user, self.backend._use_technical_user_if_set().env.user
        )
        # Finally remove the technical user
        self.env.user.company_id.write({"user_tech_id": False})
        user = self.env.user
        self.assertEqual(
            user, self.backend._use_technical_user_if_set().env.user
        )
        return
