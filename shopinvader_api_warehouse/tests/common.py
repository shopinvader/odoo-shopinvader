# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase


class WarehouseCaseCommon(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 1", "code": "WH1"}
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 2", "code": "WH2"}
        )
