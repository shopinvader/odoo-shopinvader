# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class BackendCase(CommonCase):
    def _bind_all_product(self):
        self.backend.bind_all_product()
        return (
            self.env["product.template"].search_count(
                [("sale_ok", "=", True)]
            ),
            self.env["shopinvader.product"].search_count([]),
        )

    def _bind_all_category(self):
        self.backend.bind_all_category()
        return (
            self.env["product.category"].search_count([]),
            self.env["shopinvader.category"].search_count([]),
        )

    def test_bind_all_product(self):
        self.assertEqual(*self._bind_all_product())

    def test_rebind_all_product(self):
        self._bind_all_product()
        self.env["shopinvader.variant"].search([], limit=1).unlink()
        self.assertEqual(*self._bind_all_product())

    def test_bind_all_category(self):
        self.assertEqual(*self._bind_all_category())

    def test_rebind_all_category(self):
        self._bind_all_category()
        self.env["shopinvader.category"].search([], limit=1).unlink()
        self.assertEqual(*self._bind_all_category())
