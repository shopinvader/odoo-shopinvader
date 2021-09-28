# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _check_company_auto = True

    shopinvader_company_backend_id = fields.Many2one(
        "shopinvader.backend",
        string="Company Shopinvader Backend",
        help="Your main Shopinvader backend for this company.\n"
        "If set, it allows to easily manage your Shopinvader bindings.",
        check_company=True,
    )
