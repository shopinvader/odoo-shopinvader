# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class LocoCommonCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super(LocoCommonCase, self).setUp(*args, **kwargs)
        self.base_url = self.backend.location + "/locomotive/api/v3"
