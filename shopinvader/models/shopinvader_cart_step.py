# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderCartStep(models.Model):
    _name = "shopinvader.cart.step"
    _description = "Shopinvader Cart Step"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
