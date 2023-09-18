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

    def test_binding1(self):
        """
        Test the binding by using the shopinvader.partner.binding wizard.
        :return:
        """
        shopinv_partner = self.partner._get_invader_partner(self.backend)
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
        shopinv_partner = self.partner._get_invader_partner(self.backend)
        # As we set bind = False, we check if the binding is not executed.
        self.assertFalse(shopinv_partner)
        wizard.binding_lines.write({"bind": True})
        wizard.action_apply()
        shopinv_partner = self.partner._get_invader_partner(self.backend)
        # But now we set bind = True so we check if it's done.
        self.assertTrue(shopinv_partner)
        return
