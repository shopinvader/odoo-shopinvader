# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class TestCustomer(CommonCase):

    def setUp(self, *args, **kwargs):
        super(TestCustomer, self).setUp(*args, **kwargs)
        with self.work_on_services(
                partner=None,
                shopinvader_session=self.shopinvader_session) as work:
            self.service = work.component(usage='customer')
