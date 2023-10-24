# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class CommonMassMailingCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mailing_list = cls.env.ref("mass_mailing.mailing_list_data")
        cls.mailing_contact = cls.env["mailing.contact"].create(
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "list_ids": [(6, 0, [cls.mailing_list.id])],
            }
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services() as work:
            self.service = work.component(usage="mailing_lists")

    def _get_subscription(self, mailing_list, email):
        return self.env["mailing.contact.subscription"].search(
            [
                ("list_id", "=", mailing_list.id),
                ("contact_id.email", "=", email),
            ]
        )
