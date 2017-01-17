# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AttachmentMedia(models.Model):
    _inherit = 'ir.attachment.media'

    locomotive_bind_ids = fields.One2many(
        'locomotive.media',
        'record_id',
        string='Locomotive Binding')


class LocomotiveMedia(models.Model):
    _name = 'locomotive.media'
    _inherit = 'locomotive.binding'
    _inherits = {'ir.attachment.media': 'record_id'}

    record_id = fields.Many2one(
        'ir.attachment.media',
        required=True,
        ondelete='cascade')
    url = fields.Char()

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A media can only have one binding by backend.'),
    ]
