# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class GoogleCategory(models.Model):
    _name = 'google.category'
    _description = 'Google Category'
    _order = 'google_id'

    name = fields.Char(translate=True)
    google_id = fields.Integer()

    _sql_constraints = [
        ('record_uniq', 'unique(google_id)',
         'Google category id must be uniq.')
        ]
