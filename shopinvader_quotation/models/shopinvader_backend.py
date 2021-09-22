# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    quotation_expose_all = fields.Boolean(
        string="Expose all quotations",
        help="Include quotations not bound to specific backends. ",
        default=True,
    )
