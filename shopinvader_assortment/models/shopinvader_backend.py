# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    product_manual_binding = fields.Boolean(default=True)
    product_assortment_ids = fields.Many2many(
        string="Product Assortments",
        comodel_name="ir.filters",
        help="Bind only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )

    def _autobind_product_from_assortment(self):
        self.ensure_one()
        product_obj = self.env["product.product"]
        shopinvader_variant_obj = self.env["shopinvader.variant"]
        binding_wizard_obj = self.env["shopinvader.variant.binding.wizard"]
        unbinding_wizard_obj = self.env["shopinvader.variant.unbinding.wizard"]
        global_assortment_products = product_obj
        global_variant_bound = shopinvader_variant_obj.search(
            [("backend_id", "=", self.id)]
        )
        global_products_bound = global_variant_bound.mapped("record_id")
        for assortment in self.product_assortment_ids:
            assortment_domain = assortment._get_eval_domain()
            assortment_products = product_obj.search(assortment_domain)
            global_assortment_products |= assortment_products
        products_to_bind = global_assortment_products - global_products_bound
        products_to_unbind = global_products_bound - global_assortment_products
        variants_to_unbind = global_variant_bound.filtered(
            lambda x: x.record_id.id in products_to_unbind.ids
        )

        if products_to_bind:
            binding_wizard = binding_wizard_obj.create(
                {
                    "backend_id": self.id,
                    "product_ids": [(6, 0, products_to_bind.ids)],
                }
            )
            binding_wizard.bind_products()

        if variants_to_unbind:
            unbinding_wizard = unbinding_wizard_obj.create(
                {"shopinvader_variant_ids": [(6, 0, variants_to_unbind.ids)]}
            )
            unbinding_wizard.unbind_products()

    @api.model
    def autobind_product_from_assortment(self, domain=None):
        if domain is None:
            domain = []

        domain = expression.AND(
            [domain, [("product_manual_binding", "!=", True)]]
        )

        for backend in self.search(domain):
            backend._autobind_product_from_assortment()

    def force_recompute_all_binding_index(self):
        records = self.filtered(
            lambda r: not r.product_manual_binding and r.product_assortment_ids
        )
        for record in records:
            record._autobind_product_from_assortment()
        return super().force_recompute_all_binding_index()
