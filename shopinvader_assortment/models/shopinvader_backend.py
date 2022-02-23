# Copyright 2018 ACSONE SA/NV
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    product_manual_binding = fields.Boolean(default=True)
    product_assortment_id = fields.Many2one(
        string="Product Assortment",
        comodel_name="ir.filters",
        help="Bind only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )

    @api.constrains("product_manual_binding", "product_assortment_id")
    def _check_product_assortment_id(self):
        if not all(
            rec.product_manual_binding or rec.product_assortment_id for rec in self
        ):
            raise ValidationError(
                _("Product Assortment is required for automatic binding")
            )

    def _autobind_product_from_assortment(self):
        self.ensure_one()
        if not self.product_assortment_id:
            return
        product_obj = self.env["product.product"]
        shopinvader_variant_obj = self.env["shopinvader.variant"]
        binding_wizard_obj = self.env["shopinvader.variant.binding.wizard"]
        unbinding_wizard_obj = self.env["shopinvader.variant.unbinding.wizard"]
        assortment_domain = self.product_assortment_id._get_eval_domain()
        assortment_products = product_obj.search(assortment_domain)
        variants_bound = shopinvader_variant_obj.search([("backend_id", "=", self.id)])
        products_bound = variants_bound.mapped("record_id")
        products_to_bind = assortment_products - products_bound
        products_to_unbind = products_bound - assortment_products
        variants_to_unbind = variants_bound.filtered(
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
            [
                domain,
                [
                    ("product_manual_binding", "!=", True),
                    ("product_assortment_id", "!=", False),
                ],
            ]
        )
        for backend in self.search(domain):
            backend._autobind_product_from_assortment()
