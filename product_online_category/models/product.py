# -*- coding: utf-8 -*-
# © 2017-2018 Akretion (http://www.akretion.com)
# Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    type = fields.Selection(selection_add=[("shop", "Online Shop")])


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_ids = fields.Many2many(
        string="Online Shop Categories",
        domain=[("type", "=", "shop")],
        track_visibility="onchange",
    )
