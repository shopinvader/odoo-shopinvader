# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from itertools import groupby

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero, float_round

from .tools import sanitize_attr_name


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"
    _inherits = {
        "shopinvader.product": "shopinvader_product_id",
        "product.product": "record_id",
    }
    _check_company_auto = True

    default_code = fields.Char(related="record_id.default_code", store=True)
    shopinvader_product_id = fields.Many2one(
        "shopinvader.product",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    tmpl_record_id = fields.Many2one(
        string="Product template",
        related="shopinvader_product_id.record_id",
        store=True,
        index=True,
        check_company=True,
    )
    record_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    variant_count = fields.Integer(
        related="product_variant_count", string="Shopinvader Variant Count"
    )
    variant_attributes = fields.Serialized(
        compute="_compute_variant_attributes", string="Shopinvader Attributes"
    )
    main = fields.Boolean(compute="_compute_main_product")
    active = fields.Boolean(
        default=True,
        compute="_compute_active",
        store=True,
        readonly=False,
    )
    price = fields.Serialized(compute="_compute_price", string="Shopinvader Price")
    short_name = fields.Char(compute="_compute_names")
    full_name = fields.Char(compute="_compute_names")
    # Special case for company_id, as it's present in both inherits models
    company_id = fields.Many2one(related="shopinvader_product_id.company_id")
    # As field is defined on product.template, avoid 'inherits' bypass
    description = fields.Html(
        related="shopinvader_product_id.description", readonly=False
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_attribute_value_ids",
        readonly=True,
    )

    @api.depends("shopinvader_product_id.active", "record_id.active")
    def _compute_active(self):
        """Deactivate bindings if related records are archived"""
        for rec in self:
            rec.active = (
                rec.active
                and rec.shopinvader_product_id.active
                and rec.record_id.active
            )

    @api.depends("product_template_attribute_value_ids")
    def _compute_attribute_value_ids(self):
        for record in self:
            record.attribute_value_ids = record.mapped(
                "product_template_attribute_value_ids." "product_attribute_value_id"
            )

    @contextmanager
    def _action_product_toggle_active(self):
        """
        Action a deactivation of a variant, if every variants are disabled:
        disable the product too.
        Also when a variant is enabled, the related shopinvader product
        should be re-enabled too.
        :return:
        """
        product_active_dict = {
            p: p.active for p in self.mapped("shopinvader_product_id")
        }
        yield
        to_activate_ids = set()
        to_inactivate_ids = set()
        for variant in self:
            shopinv_product = variant.shopinvader_product_id
            if variant.active:
                # If the variant is active and the related shop. product is
                # not active, we have to active it.
                if not shopinv_product.active:
                    to_activate_ids.add(shopinv_product.id)
                continue
            # If the product is already disabled, we don't have anything to do!
            if not product_active_dict.get(shopinv_product, True):
                continue
            # If every variants of the product are disabled
            # (The product is enable; checked by previous IF).
            if all([not v.active for v in shopinv_product.shopinvader_variant_ids]):
                to_inactivate_ids.add(shopinv_product.id)
        if to_activate_ids:
            self.env["shopinvader.product"].browse(to_activate_ids).write(
                {"active": True}
            )
        if to_inactivate_ids:
            self.env["shopinvader.product"].browse(to_inactivate_ids).write(
                {"active": False}
            )

    def write(self, vals):
        """
        Inherit to manage behaviour when the variant is disabled.
        We may have to disable also the shopinvader.product
        :param vals: dict
        :return: bool
        """
        with self._action_product_toggle_active():
            result = super(ShopinvaderVariant, self).write(vals)
        return result

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
        attributes = self.attribute_value_ids
        short_name = ", ".join(attributes.mapped("name"))
        full_name = self.shopinvader_display_name
        if short_name:
            full_name += " (%s)" % short_name
        return full_name, short_name

    def _compute_names(self):
        for record in self:
            (
                record.full_name,
                record.short_name,
            ) = record._prepare_variant_name_and_short_name()

    def _compute_price(self):
        for record in self:
            record.price = record._get_all_price()

    def _get_all_price(self):
        self.ensure_one()
        res = {}
        pricelist = self.backend_id.pricelist_id
        default_role = self.backend_id.customer_default_role
        if pricelist:
            res[default_role] = self._get_price(
                pricelist=pricelist, company=self.backend_id.company_id
            )
        return res

    def _compute_variant_attributes(self):
        for record in self:
            variant_attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                variant_attributes[sanitized_key] = att_value.name
            record.variant_attributes = variant_attributes

    def _get_price(self, qty=1.0, pricelist=None, fposition=None, company=None):
        """Computes the product prices

        :param qty:         The product quantity, used to apply pricelist rules.
        :param pricelist:   Optional. Get prices for a specific pricelist.
        :param fposition:   Optional. Apply fiscal position to product taxes.
        :param company:     Optional.

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
        taxes = fposition.map_tax(taxes, product) if fposition else taxes
        # Set context. Some of the methods used here depend on these values
        product_context = dict(
            self.env.context,
            quantity=qty,
            pricelist=pricelist.id if pricelist else None,
            fiscal_position=fposition,
        )
        product = product.with_context(**product_context)
        pricelist = pricelist.with_context(**product_context) if pricelist else None
        # If we have a pricelist, use product.price as it already accounts
        # for pricelist rules and quantity (in context)
        price_unit = product.price if pricelist else product.lst_price
        price_unit = AccountTax._fix_tax_included_price_company(
            price_unit, product.taxes_id, taxes, company
        )
        res = {
            "value": price_unit,
            "tax_included": any(tax.price_include for tax in taxes),
            # Default values in case price.discuont_policy != "without_discount"
            "original_value": price_unit,
            "discount": 0.0,
        }
        # Handle pricelists.discount_policy == "without_discount"
        if pricelist and pricelist.discount_policy == "without_discount":
            # Get the price rule
            price_unit, rule_id = pricelist.get_product_price_rule(product, qty, None)
            # Get the price before applying the pricelist
            SaleOrderLine = self.env["sale.order.line"].with_context(**product_context)
            original_price_unit, currency = SaleOrderLine._get_real_price_currency(
                product, rule_id, qty, product.uom_id, pricelist.id
            )
            price_dp = self.env["decimal.precision"].precision_get("Product Price")
            # Convert currency if necessary
            if (
                not float_is_zero(original_price_unit, precision_digits=price_dp)
                and pricelist.currency_id != currency
            ):
                original_price_unit = currency._convert(
                    original_price_unit,
                    pricelist.currency_id,
                    company or self.env.company,
                    fields.Date.today(),
                )
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
            res.update(
                {
                    "original_value": original_price_unit,
                    "discount": discount,
                }
            )
        return res

    def _compute_main_product(self):
        # Respect same order.
        order_by = [x.strip() for x in self.env["product.product"]._order.split(",")]
        fields_to_read = ["tmpl_record_id"] + order_by
        tmpl_ids = self.mapped("tmpl_record_id").ids
        # Use sudo to bypass permissions (we don't care)
        _variants = self.sudo().search(
            [("tmpl_record_id", "in", tmpl_ids)], order="tmpl_record_id"
        )
        # Use `load=False` to not load template name
        variants = _variants.read(fields_to_read, load=False)
        var_by_tmpl = groupby(variants, lambda x: x["tmpl_record_id"])

        def pick_1st_variant(prods):
            # NOTE: if the order is changed by adding `asc/desc` this can be broken
            # but it's very unlikely that the default order for product.product
            # will be changed.
            def get_value(record, key):
                if record[key] is False and self._fields[key].type in ("char", "text"):
                    return ""
                else:
                    return record[key]

            ordered = sorted(
                prods, key=lambda var: [get_value(var, x) for x in order_by]
            )
            return ordered[0].get("id") if ordered else None

        main_by_tmpl = {
            tmpl: pick_1st_variant(tuple(prods)) for tmpl, prods in var_by_tmpl
        }
        for record in self:
            record.main = main_by_tmpl.get(record.tmpl_record_id.id) == record.id

    def get_shop_data(self):
        """Return product data for the shop."""
        return self._get_shop_data()

    def _get_shop_data(self):
        """Compute shop data base_jsonify parser."""
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant").sudo()
        return self.jsonify(exporter.get_json_parser(), one=True)
