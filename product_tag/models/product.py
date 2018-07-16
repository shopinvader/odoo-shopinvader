# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
	"""Enhance the object to add feature."""

    _inherit = 'product.product'

    tag_ids = fields.Many2many(
        'product.tag',
        string="Tags")


class ProductTag(models.Model):
	"""Add new object to add tags in Product Variant."""

    _name = 'product.tag'

    name = fields.Char(translate=True, required=True)
    code = fields.Char(required=True)
