# Copyright 2018 ACSONE SA/NV
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class SeBackend(models.Model):
    _inherit = "se.backend"

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
        assortment_domain = self.product_assortment_id._get_eval_domain()
        assortment_products = product_obj.search(assortment_domain)
        product_indexes = self.index_ids.filtered(
            lambda i: i.model_id.model == "product.product"
        )
        products_bound = (
            product_indexes.binding_ids.record
            if product_indexes.binding_ids
            else product_obj
        )
        products_to_unbind = products_bound - assortment_products
        assortment_products._add_to_index(product_indexes)
        products_to_unbind._remove_from_index(product_indexes)

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
