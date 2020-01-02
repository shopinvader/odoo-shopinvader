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

    def unbind_products(self):
        for wizard in self:
            wizard.shopinvader_variant_ids.write({"active": False})

    @api.model
    def unbind_langs(self, backend, lang_ids):
        """
        Unbind the binded shopinvader.variant for the given lang
        :param backend: backend record
        :param lang_ids: list of lang ids we must ensure that no more binding
                          exists
        :return:
        """
        shopinvader_variant_ids = self.env["shopinvader.variant"].search(
            [("lang_id", "in", lang_ids), ("backend_id", "=", backend.id)]
        )
        # use in memory record to avoid the creation of useless records into
        # the database
        wiz = self.create({"shopinvader_variant_ids": shopinvader_variant_ids})
        wiz.unbind_products()
