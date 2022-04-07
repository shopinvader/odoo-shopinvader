# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    workflow_process_id = fields.Many2one(
        comodel_name="sale.workflow.process",
        string="Automatic Workflow",
        help="Sales Orders created by this backend will use this workflow",
        ondelete="restrict",
    )
