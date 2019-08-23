# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2019 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ShopinvaderPartner(models.Model):
    _name = "shopinvader.partner"
    _inherit = ["shopinvader.partner", "shopinvader.client.binding"]
