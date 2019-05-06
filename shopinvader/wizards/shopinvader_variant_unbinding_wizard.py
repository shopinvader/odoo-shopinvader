# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariantUnbindingWizard(models.TransientModel):

    _name = "shopinvader.variant.unbinding.wizard"
    _description = "Wizard to unbind products from a shopinvader backend"

    shopinvader_variant_ids = fields.Many2many(
        string="Products",
        comodel_name="shopinvader.variant",
        relation="shopinvader_variant_unbind_wizard_rel",
        ondelete="cascade",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderVariantUnbindingWizard, self).default_get(
            fields_list
        )
        shopinvader_variant_ids = self.env.context.get("active_ids", False)
        if shopinvader_variant_ids:
            res["shopinvader_variant_ids"] = shopinvader_variant_ids
        return res

    @api.multi
    def unbind_products(self):
        for wizard in self:
            wizard.shopinvader_variant_ids.write({"active": False})
