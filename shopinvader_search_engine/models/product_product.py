# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def unlink(self):
        # Call unlink manually to be sure to trigger
        # shopinvader variant unlink constraint
        self.mapped("shopinvader_bind_ids").unlink()
        return super(ProductProduct, self).unlink()
