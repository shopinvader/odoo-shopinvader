# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import urllib

GOOGLE_CATEG_URL =\
    "http://www.google.com/basepages/producttype/taxonomy-with-ids.%s.txt"


class ImportGoogleCategory(models.TransientModel):
    _name = 'import.google.category'
    _description = 'Import Google Category'

    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        required=True)

    @api.multi
    def run(self):
        self.ensure_one()
        categ_obj = self.env['google.category'].with_context(
            lang=self.lang_id.code)
        code = self.lang_id.code.replace('_', '-')
        res = urllib.urlopen(GOOGLE_CATEG_URL % code).read().splitlines()
        res.pop(0)
        for line in res:
            google_id, name = line.split(' - ', 1)
            google_id = int(google_id)
            categ = categ_obj.search([('google_id', '=', google_id)])
            if categ:
                categ.write({'name': name})
            else:
                categ_obj.create({
                    'name': name,
                    'google_id': google_id,
                    })
