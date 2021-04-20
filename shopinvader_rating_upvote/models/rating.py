# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class RatingVote(models.Model):
    _inherit = "rating.rating"

    partner_ids = fields.Many2many(comodel_name="res.partner", string="Partners")
    upvotes = fields.Integer(default=0, compute="_compute_nb_upvotes")

    def _compute_nb_upvotes(self):
        self.upvotes = len(self.partner_ids)
