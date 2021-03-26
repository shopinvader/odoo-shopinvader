# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestGuestBinding(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGuestBinding, cls).setUpClass()
        cls.wizard_obj = cls.env["shopinvader.partner.binding"]
        cls.guest_partner = cls.env.ref(
            "shopinvader_guest_mode.partner_guest_1"
        )
        cls.backend_2 = cls.env.ref("shopinvader.backend_2")

    def test_guest_binding(self):
        # Check a partner that is guest on a backend
        # Check the 'Bind' checkbox on the wizard
        # The partner is no more guest
        self.assertTrue(self.guest_partner.shopinvader_bind_ids.is_guest)
        self.wizard = self.wizard_obj.with_context(
            active_ids=self.guest_partner.ids, active_model="res.partner"
        ).new({})
        self.wizard.shopinvader_backend_id = self.backend_2
        self.wizard._onchange_shopinvader_backend_id()
        # Check if one line is created with the partner
        self.assertEquals(1, len(self.wizard.binding_lines))
        self.assertEquals(
            self.guest_partner, self.wizard.binding_lines.partner_id
        )
        self.wizard.binding_lines.bind = True
        vals = self.wizard._convert_to_write(self.wizard._cache)
        self.wizard = self.wizard_obj.create(vals)
        self.wizard.action_apply()
        # Check if the guest is no more
        self.assertFalse(self.guest_partner.shopinvader_bind_ids.is_guest)

        # Check if a new launch of the wizard generates no lines
        self.wizard = self.wizard_obj.with_context(
            active_ids=self.guest_partner.ids, active_model="res.partner"
        ).new({})
        self.wizard.shopinvader_backend_id = self.backend_2
        self.wizard._onchange_shopinvader_backend_id()
        self.assertEquals(0, len(self.wizard.binding_lines))
