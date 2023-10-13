# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero

from odoo.addons.base_sparse_field.models.fields import Serialized

from ..utils import float_round
from .tools import sanitize_attr_name


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_attributes = Serialized(
        compute="_compute_variant_attributes", string="Shopinvader Attributes"
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_attribute_value_ids",
        readonly=True,
    )
    short_name = fields.Char(compute="_compute_names")
    full_name = fields.Char(compute="_compute_names")
    main = fields.Boolean(compute="_compute_main_product")
    price = Serialized(compute="_compute_price", string="Shopinvader Price")

    def _compute_variant_attributes(self):
        for record in self:
            variant_attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                variant_attributes[sanitized_key] = att_value.name
            record.variant_attributes = variant_attributes

    @api.depends("product_template_attribute_value_ids")
    def _compute_attribute_value_ids(self):
        for record in self:
            record.attribute_value_ids = record.mapped(
                "product_template_attribute_value_ids.product_attribute_value_id"
            )

    def _prepare_variant_name_and_short_name(self):
        self.ensure_one()
        attributes = self.attribute_value_ids
        short_name = ", ".join(attributes.mapped("name"))
        full_name = self.display_name
        if short_name:
            full_name += " (%s)" % short_name
        return full_name, short_name

    def _compute_names(self):
        for record in self:
            (
                record.full_name,
                record.short_name,
            ) = record._prepare_variant_name_and_short_name()

    @api.model
    def _get_shopinvader_product_variants(self, product_ids):
        # Use sudo to bypass permissions (we don't care)
        return self.sudo().search(
            [("product_tmpl_id", "in", product_ids)], order="product_tmpl_id"
        )

    def _compute_main_product(self):
        # Respect same order.
        order_by = [x.strip() for x in self.env["product.product"]._order.split(",")]
        fields_to_read = ["product_tmpl_id"] + [f.split(" ")[0] for f in order_by]
        product_ids = self.mapped("product_tmpl_id").ids
        _variants = self._get_shopinvader_product_variants(product_ids)
        # Use `load=False` to not load template name
        variants = _variants.read(fields_to_read, load=False)
        var_by_product = groupby(variants, lambda x: x["product_tmpl_id"])

        def pick_1st_variant(variants):
            def get_value(record, key):
                if record[key] is False and self._fields[key].type in ("char", "text"):
                    return ""
                else:
                    return record[key]

            for order_key in reversed(order_by):
                order_key_split = order_key.split(" ")
                reverse = len(order_key_split) > 1 and order_key_split[1] == "desc"
                variants.sort(
                    key=lambda var: get_value(var, order_key_split[0]),
                    reverse=reverse,
                )
            return variants[0].get("id") if variants else None

        main_by_product = {
            product: pick_1st_variant(list(variants))
            for product, variants in var_by_product
        }
        for record in self:
            record.main = main_by_product.get(record.product_tmpl_id.id) == record.id

    @api.depends_context("pricelist", "default_role", "fposition", "company", "date")
    def _compute_price(self):
        for record in self:
            record.price = record._get_all_price()

    def _get_all_price(self):
        self.ensure_one()
        res = {}
        pricelist = self._context.get("pricelist")
        default_role = self._context.get("default_role", "default")
        if pricelist:
            fposition = self._context.get("fposition")
            company = self._context.get("company")
            date = self._context.get("date")
            res[default_role] = self._get_price(
                pricelist=pricelist, fposition=fposition, company=company, date=date
            )
        return res

    def _get_price(
        self, qty=1.0, pricelist=None, fposition=None, company=None, date=None
    ):
        """Computes the product prices

        :param qty:         The product quantity, used to apply pricelist rules.
        :param pricelist:   Optional. Get prices for a specific pricelist.
        :param fposition:   Optional. Apply fiscal position to product taxes.
        :param company:     Optional.
        :param date:        Optional.

        :returns: dict with the following keys:

            <value>                 The product unitary price
            <tax_included>          True if product taxes are included in <price>.

            If the pricelist.discount_policy is "without_discount":
            <original_value>        The original price (before pricelist is applied).
            <discount>              The discounted percentage.
        """
        self.ensure_one()
        AccountTax = self.env["account.tax"]
        product = self.record_id
        # Apply company
        product = product.with_company(company) if company else product
        company = company or self.env.company
        # Always filter taxes by the company
        taxes = product.taxes_id.filtered(lambda tax: tax.company_id == company)
        # Apply fiscal position
        taxes = fposition.map_tax(taxes) if fposition else taxes
        # Set context. Some of the methods used here depend on these values
        product_context = dict(
            self.env.context,
            quantity=qty,
            pricelist=pricelist.id if pricelist else None,
            fiscal_position=fposition,
            date=date,
        )
        product = product.with_context(**product_context)
        pricelist = pricelist.with_context(**product_context) if pricelist else None
        price_unit = (
            pricelist._get_product_price(product, qty, date=date)
            if pricelist
            else product.lst_price
        )
        price_unit = AccountTax._fix_tax_included_price_company(
            price_unit, product.taxes_id, taxes, company
        )
        price_dp = self.env["decimal.precision"].precision_get("Product Price")
        price_unit = float_round(price_unit, price_dp)
        res = {
            "value": price_unit,
            "tax_included": any(tax.price_include for tax in taxes),
            # Default values in case price.discount_policy != "without_discount"
            "original_value": price_unit,
            "discount": 0.0,
        }
        # Handle pricelists.discount_policy == "without_discount"
        if pricelist and pricelist.discount_policy == "without_discount":
            # Get the price rule
            price_unit, rule_id = pricelist._get_product_price_rule(
                product, qty, date=date
            )
            # Get the price before applying the pricelist
            original_price_unit = product.lst_price
            price_dp = self.env["decimal.precision"].precision_get("Product Price")
            # Compute discount
            if not float_is_zero(
                original_price_unit, precision_digits=price_dp
            ) and float_compare(
                original_price_unit, price_unit, precision_digits=price_dp
            ):
                discount = (
                    (original_price_unit - price_unit) / original_price_unit * 100
                )
                # Apply the right precision on discount
                discount_dp = self.env["decimal.precision"].precision_get("Discount")
                discount = float_round(discount, discount_dp)
            else:
                discount = 0.00
            # Compute prices
            original_price_unit = AccountTax._fix_tax_included_price_company(
                original_price_unit, product.taxes_id, taxes, company
            )
            original_price_unit = float_round(original_price_unit, price_dp)
            res.update(
                {
                    "original_value": original_price_unit,
                    "discount": discount,
                }
            )
        return res
