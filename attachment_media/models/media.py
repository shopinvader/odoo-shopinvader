# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MediaMedia(models.Model):
    _name = 'ir.attachment.media'
    _description = 'Media Attachment'
    _inherits = {'ir.attachment': 'attachment_id'}

    attachment_id = fields.Many2one(
        'ir.attachment',
        required=True,
        ondelete='cascade',
        help="Link to ir.attachment model")

    # If you want to add new type base default please do a PR
    media_type = fields.Selection([
        ('certification', 'Certification'),
        ('packaging', 'Packaging'),
        ('specification', 'Specification'),
        ('instruction', 'Instruction'),
        ('warranty', 'Warranty'),
        ('security', 'Security'),
        ('faq', 'FAQ'),
        ])
