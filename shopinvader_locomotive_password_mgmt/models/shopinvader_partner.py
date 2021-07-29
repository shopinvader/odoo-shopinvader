# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderPartner(models.Model):

    _inherit = "shopinvader.partner"

    password = fields.Char(copy=False)
