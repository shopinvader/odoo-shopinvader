# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class SeBackend(models.Model):
    _inherit = 'se.backend'

    product_stock_field_id = fields.Many2one(
        "ir.model.fields",
        "Product stock field",
        domain=[
            ('ttype', 'in', ['float', 'integer']),
            ('model_id.model', '=', 'product.product'),
        ],
        help="Field used to have the current stock of a product.product",
    )
    export_stock_key = fields.Char(
        help="Key used into the export to contains the stock value defined by "
             "the Product stock field.\n"
             "This stock value export is disabled for the current backend if "
             "this key is not set",
    )

    @api.multi
    @api.constrains('export_stock_key', 'product_stock_field_id')
    def _constraint_key_field_set(self):
        """
        Constraint to ensure that product_stock_field_id is set when the
        export_stock_key field is filled.
        :return:
        """
        bad_backends = self.filtered(
            lambda b: b.export_stock_key and not b.product_stock_field_id)
        bad_backends = bad_backends.with_prefetch(self._prefetch)
        if bad_backends:
            details = "\n- ".join(bad_backends.display_name)
            message = _("Please set a stock field to fill the Export stock "
                        "key for these backends:\n- %s") % details
            raise exceptions.ValidationError(message)
