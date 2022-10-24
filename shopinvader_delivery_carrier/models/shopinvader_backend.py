# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    delivery_order_states = fields.Selection(
        string="Visible delivery order states",
        selection=[
            ("", "All"),
            ("confirmed|waiting|assigned|done", "All but draft"),
            ("assigned|done", "Ready and done"),
        ],
        default="assigned|done",
        help="""Allows to filter out pickings based on state
            All: publish all pickings
            All but draft: filter out only draft and cancels pickings
            Ready and done: publish only assigned and done pickings
        """,
    )

    def _get_visible_delivery_order_states(self):
        if not self.delivery_order_states:
            return []
        return self.delivery_order_states.split("|")
