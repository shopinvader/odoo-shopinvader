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

    def _autobind_product_from_assortment(self, domain_product=None):
        self.ensure_one()
        if not self.product_assortment_id:
            return
        if domain_product is None:
            domain_product = []
        domain_assortment = self.product_assortment_id._get_eval_domain()
        domain = expression.AND([domain_assortment, domain_product])
        products_to_bind = self._get_product_to_bind(domain)
        products_to_unbind = self._get_product_to_unbind(domain)
        product_indexes = self.index_ids.filtered(
            lambda i: i.model_id.model == "product.product"
        )
        products_to_bind._add_to_index(product_indexes)
        products_to_unbind._remove_from_index(product_indexes)

    @api.model
    def autobind_product_from_assortment(self, domain=None, domain_product=None):
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
            backend._autobind_product_from_assortment(domain_product=domain_product)

    def _get_product_bound(self, domain):
        query = self.env["product.product"]._where_calc(domain)
        self.env["product.product"]._apply_ir_rules(query, "read")
        query.left_join(
            lhs_alias="product_product",
            lhs_column="id",
            rhs_table="se_binding",
            rhs_column="res_id",
            link="se_binding",
            extra="product_product__se_binding.res_model='product.product'",
        )
        return self.env["product.product"].browse(query)

    def _get_product_to_bind(self, domain):
        return self._get_product_bound(domain)

    def _get_product_to_unbind(self, domain):
        domain = expression.distribute_not(["!"] + domain)
        return self._get_product_bound(domain)
