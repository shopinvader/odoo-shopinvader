# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class ResPartner(models.Model):
    _inherit='res.partner'


    def _json_parser_contact(self):
        return [
            'id',
            'display_name',
            'name',
            'ref',
            'street',
            'street2',
            'zip',
            'city',
            'phone',
            ('state_id', ['name']),
            ('country_id', ['name'])
        ]

    @api.multi
    def to_json_contact(self):
        return self.jsonify(self._json_parser_contact())


