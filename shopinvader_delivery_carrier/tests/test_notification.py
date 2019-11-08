# Copyright 2019 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.tests.test_notification import (
    NotificationCaseMixin,
)


class NotificationPickingCase(CommonCase, NotificationCaseMixin):
    @classmethod
    def setUpClass(cls):
        super(NotificationPickingCase, cls).setUpClass()
        cls.cart = cls.env.ref("shopinvader.sale_order_2")
        cls.cart.action_confirm()
        cls.picking = cls.cart.picking_ids

    def test_picking_notification1(self):
        """
        Check notification on outgoing picking.
        For this case, we should have a notification
        :return:
        """
        self._init_job_counter()
        self.picking.action_done()
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self._check_notification(
            "stock_picking_outgoing_validated", self.picking
        )

    def test_picking_notification2(self):
        """
        Check notification on outgoing picking.
        For this case, the picking is outgoing but is not related to a sale
        (with backend) so it shouldn't notify anything
        :return:
        """
        picking = self.picking.copy()
        # Remove the link with procurement/sales
        picking.move_lines.write({"sale_line_id": False})
        self._init_job_counter()
        picking.action_done()
        self._check_nbr_job_created(0)

    def test_picking_notification3(self):
        """
        Check notification on outgoing picking.
        For this case, we change the picking type. So it shouldn't notify
        anything.
        :return:
        """
        self.picking.picking_type_id.write({"code": "internal"})
        self._init_job_counter()
        self.picking.action_done()
        self._check_nbr_job_created(0)
