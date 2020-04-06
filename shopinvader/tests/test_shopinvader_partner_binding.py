# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions

from .common import CommonCase


class TestShopinvaderPartnerBinding(CommonCase):
    """
    Tests for shopinvader.partner.binding
    """

    def setUp(self):
        super(TestShopinvaderPartnerBinding, self).setUp()
        self.binding_wiz_obj = self.env["shopinvader.partner.binding"]
        self.partner = self.env.ref("base.res_partner_2")

    def _get_shopinvader_partner(self, partner, backend):
        """
        Get the shopinvader partner related to given partner on given backend.
        :param partner: res.partner
        :param backend: shopinvader.backend
        :return: shopinvader.partner
        """
        shopinv_partner = partner.shopinvader_bind_ids.filtered(
            lambda r, b=backend: r.backend_id == b
        )
        return shopinv_partner

    def test_binding1(self):
        """
        Test the binding by using the shopinvader.partner.binding wizard.
        :return:
        """
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # This partner shouldn't be already binded
        self.assertFalse(shopinv_partner)
        context = self.env.context.copy()
        context.update(
            {
                "active_id": self.partner.id,
                "active_ids": self.partner.ids,
                "active_model": self.partner._name,
            }
        )
        wizard_obj = self.binding_wiz_obj.with_context(context)
        fields_list = wizard_obj.fields_get().keys()
        values = wizard_obj.default_get(fields_list)
        values.update({"shopinvader_backend_id": self.backend.id})
        wizard = wizard_obj.create(values)
        wizard._onchange_shopinvader_backend_id()
        wizard.binding_lines.write({"bind": False})
        with self.assertRaises(exceptions.UserError) as e:
            wizard.action_apply()
        self.assertIn("unbind is not implemented", e.exception.name)
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # As we set bind = False, we check if the binding is not executed.
        self.assertFalse(shopinv_partner)
        wizard.binding_lines.write({"bind": True})
        wizard.action_apply()
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # But now we set bind = True so we check if it's done.
        self.assertTrue(shopinv_partner)
        return

    def test_binding_email_uppercase(self):
        """
        Test the binding on a partner with an email in upper case.
        The email should be updated with lower case.
        :return:
        """
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        lower_email = self.partner.email.lower()
        # This partner shouldn't be already bound
        self.assertFalse(shopinv_partner)
        context = self.env.context.copy()
        self.partner.write({"email": lower_email.upper()})
        context.update(
            {
                "active_id": self.partner.id,
                "active_ids": self.partner.ids,
                "active_model": self.partner._name,
            }
        )
        wizard_obj = self.binding_wiz_obj.with_context(context)
        fields_list = wizard_obj.fields_get().keys()
        values = wizard_obj.default_get(fields_list)
        values.update({"shopinvader_backend_id": self.backend.id})
        wizard = wizard_obj.create(values)
        wizard._onchange_shopinvader_backend_id()
        wizard.binding_lines.write({"bind": True})
        wizard.action_apply()
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # Ensure the binding is done
        self.assertTrue(shopinv_partner)
        self.assertEquals(shopinv_partner.email, lower_email)

    def test_binding_multicompany(self):
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # This partner shouldn't be already binded
        self.assertFalse(shopinv_partner)
        context = self.env.context.copy()
        context.update(
            {
                "active_id": self.partner.id,
                "active_ids": self.partner.ids,
                "active_model": self.partner._name,
            }
        )
        wizard_obj = self.binding_wiz_obj.with_context(context)
        fields_list = wizard_obj.fields_get().keys()
        values = wizard_obj.default_get(fields_list)
        values.update({"shopinvader_backend_id": self.backend.id})
        wizard = wizard_obj.create(values)
        wizard._onchange_shopinvader_backend_id()
        wizard.binding_lines.write({"bind": True})
        wizard.action_apply()
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend
        )
        # But now we set bind = True so we check if it's done.
        self.assertTrue(shopinv_partner)

        # Switch to Company Liege
        company_before = self.env.user.company_id
        self.env.user.write({"company_id": self.company_liege.id})
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend_liege
        )
        # This partner shouldn't be already binded to Liege
        self.assertFalse(shopinv_partner)

        context = self.env.context.copy()
        context.update(
            {
                "active_id": self.partner.id,
                "active_ids": self.partner.ids,
                "active_model": self.partner._name,
            }
        )
        wizard_obj = self.binding_wiz_obj.with_context(context)
        fields_list = wizard_obj.fields_get().keys()
        values = wizard_obj.default_get(fields_list)
        values.update({"shopinvader_backend_id": self.backend_liege.id})
        wizard = wizard_obj.create(values)
        wizard._onchange_shopinvader_backend_id()
        wizard.binding_lines.write({"bind": True})
        wizard.action_apply()
        shopinv_partner = self._get_shopinvader_partner(
            self.partner, self.backend_liege
        )
        # But now we set bind = True so we check if it's done.
        self.assertTrue(shopinv_partner)
        self.env.user.write({"company_id": company_before.id})
