# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """existing urls should not be synced."""

    env = api.Environment(cr, SUPERUSER_ID, {})
    shop_categ = env["shopinvader.category"].search([])
    to_recompute = shop_categ.filtered(lambda x: not x.shopinvader_parent_id)
    to_recompute._compute_automatic_url_key()
