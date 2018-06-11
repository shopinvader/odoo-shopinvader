# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _description = 'Locomotive CMS Backend'
    _name = 'shopinvader.backend'
    _inherit = ['shopinvader.backend', 'connector.backend', 'keychain.backend']
    _backend_name = 'locomotivecms'

    location = fields.Char(required=True, sparse='data')
    username = fields.Char(required=True, sparse='data')
    handle = fields.Char(required=True, sparse='data')
