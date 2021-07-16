# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from itertools import groupby

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_round

from odoo.addons.queue_job.exception import RetryableJobError

from .tools import sanitize_attr_name


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"
    _inherits = {
        "shopinvader.product": "shopinvader_product_id",
        "product.product": "record_id",
    }

    default_code = fields.Char(related="record_id.default_code", store=True)
    shopinvader_product_id = fields.Many2one(
        "shopinvader.product", required=True, ondelete="cascade", index=True
    )
    tmpl_record_id = fields.Many2one(
        string="Product template",
        related="shopinvader_product_id.record_id",
        store=True,
        index=True,
    )
    record_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
        ondelete="cascade",
        index=True,
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

    # As field is defined on product.template, avoid 'inherits' bypass
    description = fields.Html(
        related="shopinvader_product_id.description", readonly=False
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_attribute_value_ids",
        readonly=True,
    )

    @api.depends("product_template_attribute_value_ids")
    def _compute_attribute_value_ids(self):
        for record in self:
            record.attribute_value_ids = record.mapped(
                "product_template_attribute_value_ids."
                "product_attribute_value_id"
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
            if all(
                [not v.active for v in shopinv_product.shopinvader_variant_ids]
            ):
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
                pricelist, None, self.backend_id.company_id
            )
        return res

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
        # Respect same order.
        order_by = [
            x.strip() for x in self.env["product.product"]._order.split(",")
        ]
        fields_to_read = ["shopinvader_product_id"] + order_by
        product_ids = self.mapped("shopinvader_product_id").ids
        # Use sudo to bypass permissions (we don't care)
        _variants = self.sudo().search(
            [("shopinvader_product_id", "in", product_ids)],
            order="shopinvader_product_id",
        )
        # Use `load=False` to not load template name
        variants = _variants.read(fields_to_read, load=False)
        var_by_product = groupby(
            variants, lambda x: x["shopinvader_product_id"]
        )

        def pick_1st_variant(variants):
            # NOTE: if the order is changed by adding `asc/desc` this can be broken
            # but it's very unlikely that the default order for product.product
            # will be changed.
            try:
                ordered = sorted(
                    variants, key=lambda var: [var[x] for x in order_by]
                )
            except TypeError as orig_exception:
                # TypeError: '<' not supported between instances of 'bool' and 'str'
                # It means we don't have all values to determine this value.
                msg = _(
                    "Cannot determine main variant for shopinvader.product ID: %s."
                    "\nAt least one variant misses one of these values: %s."
                    "\nWill try again later till 'max retries' count is reached."
                ) % (
                    variants[0]["shopinvader_product_id"],
                    ", ".join(order_by),
                )
                # This issue might depend on incomplete state of product info.
                # Eg: missing translation for variant matching current lang.
                # Let's retry later a bunch of times (5 by default).
                raise RetryableJobError(msg) from orig_exception
            return ordered[0].get("id") if ordered else None

        main_by_product = {
            product: pick_1st_variant(tuple(variants))
            for product, variants in var_by_product
        }
        for record in self:
            record.main = (
                main_by_product.get(record.shopinvader_product_id.id)
                == record.id
            )

    def get_shop_data(self):
        """Return product data for the shop."""
        return self._get_shop_data()

    def _get_shop_data(self):
        """Compute shop data base_jsonify parser."""
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        return self.jsonify(exporter.get_json_parser(), one=True)
