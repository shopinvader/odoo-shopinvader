# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class Image(models.Model):
    _inherit = 'base_multi_image.image'

    locomotivecms_bind_ids = fields.One2many(
        'locomotivecms.image',
        'record_id',
        string='Locomotive Binding')


class LocomotivecmsImage(models.Model):
    _name = 'locomotivecms.image'
    _inherit = 'locomotivecms.binding'

    record_id = fields.Many2one(
        'base_multi_image.image',
        required=True,
        ondelete='cascade')
