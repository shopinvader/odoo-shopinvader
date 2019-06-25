# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare, float_round

from .tools import sanitize_attr_name


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"
    _inherits = {
        "shopinvader.product": "shopinvader_product_id",
        "product.product": "record_id",
    }

    default_code = fields.Char(related="record_id.default_code")
    shopinvader_product_id = fields.Many2one(
        "shopinvader.product", required=True, ondelete="cascade", index=True
    )
    record_id = fields.Many2one(
        "product.product", required=True, ondelete="cascade", index=True
    )
    object_id = fields.Integer(
        compute="_compute_object_id", store=True, index=True
    )
    variant_count = fields.Integer(
        related="product_variant_count", string="Shopinvader Variant Count"
    )
    variant_attributes = fields.Serialized(
        compute="_compute_variant_attributes", string="Shopinvader Attributes"
    )
    main = fields.Boolean(compute="_compute_main_product")
    redirect_url_key = fields.Serialized(
        compute="_compute_redirect_url_key", string="Redirect Url Keys"
    )
    active = fields.Boolean(default=True)
    price = fields.Serialized(
        compute="_compute_price", string="Shopinvader Price"
    )
    short_name = fields.Char(compute="_compute_names")
    full_name = fields.Char(compute="_compute_names")

    @api.multi
    def _build_seo_title(self):
        """
        Build the SEO product name.
        Call the same function on the related shopinvader product.
        :return: str
        """
        self.ensure_one()
        return self.shopinvader_product_id._build_seo_title()

    def _prepare_variant_name_and_short_name(self):
        self.ensure_one()
        attributes = self.attribute_line_ids.filtered(
            lambda l: len(l.value_ids) > 1
        ).mapped("attribute_id")
        short_name = self.attribute_value_ids._variant_name(attributes)
        full_name = self.shopinvader_display_name
        if short_name:
            full_name += " (%s)" % short_name
        return full_name, short_name

    def _compute_names(self):
        for record in self:
            record.full_name, record.short_name = (
                record._prepare_variant_name_and_short_name()
            )

    def _compute_price(self):
        for record in self:
            record.price = record._get_all_price()

    def _get_all_price(self):
        self.ensure_one()
        res = {}
        pricelist = self.backend_id.pricelist_id
        if pricelist:
            res["default"] = self._get_price(
                pricelist, None, self.backend_id.company_id
            )
        return res

    @api.depends("record_id")
    def _compute_object_id(self):
        for record in self:
            record.object_id = record.record_id.id

    def _compute_redirect_url_key(self):
        for record in self:
            res = []
            for url in record.redirect_url_url_ids:
                res.append(url.url_key)
            record.redirect_url_key = res

    def _compute_variant_attributes(self):
        for record in self:
            variant_attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                variant_attributes[sanitized_key] = att_value.name
            record.variant_attributes = variant_attributes

    def _get_price(self, pricelist, fposition, company=None):
        self.ensure_one()
        return self._get_price_per_qty(1, pricelist, fposition, company)

    def _get_price_per_qty(self, qty, pricelist, fposition, company=None):
        product_id = self.record_id
        taxes = product_id.taxes_id.sudo().filtered(
            lambda r: not company or r.company_id == company
        )
        # get the expeced tax to apply from the fiscal position
        tax_id = fposition.map_tax(taxes, product_id) if fposition else taxes
        tax_id = tax_id and tax_id[0]
        product = product_id.with_context(
            quantity=qty, pricelist=pricelist.id, fiscal_position=fposition
        )
        final_price, rule_id = pricelist.get_product_price_rule(
            product, qty or 1.0, None
        )
        tax_included = tax_id.price_include
        account_tax_obj = self.env["account.tax"]
        # fix tax on the price
        value = account_tax_obj._fix_tax_included_price_company(
            final_price, product.taxes_id, tax_id, company
        )
        res = {
            "value": value,
            "tax_included": tax_included,
            "original_value": value,
            "discount": 0.0,
        }
        if pricelist.discount_policy == "without_discount":
            sol = self.env["sale.order.line"]
            new_list_price, currency_id = sol._get_real_price_currency(
                product, rule_id, qty or 1.0, product.uom_id, pricelist.id
            )
            # fix tax on the real price
            new_list_price = account_tax_obj._fix_tax_included_price_company(
                new_list_price, product.taxes_id, tax_id, company
            )
            product_precision = self.env["decimal.precision"].precision_get(
                "Product Price"
            )
            if (
                float_compare(
                    new_list_price, value, precision_digits=product_precision
                )
                == 0
            ):
                # Both prices are equals. Product is wihout discount, avoid
                # divide by 0 exception
                return res
            discount = (new_list_price - value) / new_list_price * 100
            # apply the right precision on discount
            dicount_precision = self.env["decimal.precision"].precision_get(
                "Discount"
            )
            discount = float_round(discount, dicount_precision)
            res.update(
                {"original_value": new_list_price, "discount": discount}
            )
        return res

    def _compute_main_product(self):
        for record in self:
            if (
                record.record_id
                == record.product_tmpl_id.product_variant_ids[0]
            ):
                record.main = True
            else:
                record.main = False
