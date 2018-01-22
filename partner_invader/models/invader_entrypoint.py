# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.server_environment import serv_config
from odoo.osv.expression import TRUE_DOMAIN, FALSE_DOMAIN

CONFIG_SECTION = 'greenbox_website'


class InvaderEntrypoint(models.Model):
    _inherit = 'invader.entrypoint'

    @api.model
    def _default_partner_model_id(self):
        return self.env.ref('base.model_res_partner')

    partner_model_id = fields.Reference(
        selection=[
            ('res.partner', 'Partner'),
        ],
        required=True,
        default=_default_partner_model_id,
    )
