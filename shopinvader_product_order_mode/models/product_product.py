# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    shop_order_mode = fields.Selection(
        selection=[("direct_sale_only", _("Direct Sale Only"))],
        string="Shopinvader Order Mode",
        store=True,
        readonly=False,
        compute="_compute_shop_order_mode",
        inverse="_inverse_shop_order_mode",
        help="Order mode for the product in Shopinvader.",
    )
    is_shop_order_mode_enabled = fields.Boolean(
        string="Template Shop Order Mode Disabled",
        related="product_tmpl_id.is_shop_order_mode_enabled_on_variant",
        store=True,
        readonly=True,
    )

    @api.depends(
        "product_tmpl_id.shop_order_mode",
        "product_tmpl_id.is_shop_order_mode_enabled_on_variant",
    )
    def _compute_shop_order_mode(self):
        for product in self:
            if not product.product_tmpl_id:
                product.shop_order_mode = False
            elif not product.product_tmpl_id.is_shop_order_mode_enabled_on_variant:
                product.shop_order_mode = product.product_tmpl_id.shop_order_mode

    def _inverse_shop_order_mode(self):
        for product in self:
            if not product.is_shop_order_mode_enabled and not self.env.context.get(
                "skip_shop_order_mode_validation"
            ):
                raise ValidationError(
                    _(
                        "Unable to modify 'shop_order_mode' on the product "
                        "'%(product_name)s' as it is blocked by the template "
                        "'%(template_name)s'."
                    )
                    % {
                        "product_name": product.name,
                        "template_name": product.product_tmpl_id.name,
                    }
                )
