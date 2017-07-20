# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
from openerp.exceptions import ValidationError


class RoleCase(CommonCase):

    def test_unique_default_role(self):
        role = self.env.ref('shopinvader.role_3')
        with self.assertRaises(ValidationError):
            role.default = True

    def test_unique_pricelist_fposition_role(self):
        role = self.env.ref('shopinvader.role_3')
        fposition = self.env.ref('shopinvader.fiscal_position_0')
        with self.assertRaises(ValidationError):
            role.fiscal_position_ids = [(4, fposition.id)]
