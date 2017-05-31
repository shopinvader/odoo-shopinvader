# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unidecode import unidecode

from openerp import api, fields, models


def sanitize_attr_name(attribute):
    key = attribute.name
    return unidecode(key.replace(' ', '_').lower())


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.product',
        'record_id',
        string='Shopinvader Binding')

    @api.multi
    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            record.shopinvader_bind_ids.unlink()
        return super(ProductTemplate, self).unlink()


class ProductFilter(models.Model):
    _name = 'product.filter'
    _description = 'Product Filter'

    based_on = fields.Selection(
        selection=[
            ('field', 'Field'),
            ('attribute', 'Attribute')
        ],
        required=True
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        'Field',
        domain=[('model', 'in', (
            'product.template',
            'product.product',
            'shopinvader.product',
            ))])
    attribute_id = fields.Many2one(
        string='Attribute',
        comodel_name='product.attribute'
    )
    help = fields.Html(translate=True)
    name = fields.Char(translate=True, required=True)
    display_name = fields.Char(
        compute="_compute_display_name"
    )

    def _compute_display_name(self):
        for pfilter in self:
            if pfilter.based_on == 'field':
                pfilter.display_name = pfilter.field_id.name
            else:
                pfilter.display_name = sanitize_attr_name(pfilter.attribute_id)


class ShopinvaderProduct(models.Model):
    _name = 'shopinvader.product'
    _inherit = ['locomotive.binding', 'abstract.url']
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade')
    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        required=True)
    seo_title = fields.Char()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    shopinvader_variant_ids = fields.One2many(
        'shopinvader.variant',
        'shopinvader_product_id',
        'Shopinvader Variant')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A product can only have one binding by backend.'),
    ]

    def _prepare_shopinvader_variant(self, variant):
        return {
            'record_id': variant.id,
            'shopinvader_product_id': self.id,
            }

    def _create_shopinvader_variant(self):
        self.ensure_one()
        for variant in self.product_variant_ids:
            vals = self._prepare_shopinvader_variant(variant)
            self.env['shopinvader.variant'].create(vals)

    @api.model
    def create(self, vals):
        binding = super(ShopinvaderProduct, self).create(vals)
        binding._create_shopinvader_variant()
        return binding

    def _build_url_key(self):
        key = super(ShopinvaderProduct, self)._build_url_key()
        if self.default_code:
            key = '-'.join([key, self.default_code])
        return key

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(ShopinvaderProduct, self)._compute_url()

    @api.onchange('backend_id')
    def set_default_lang(self):
        self.ensure_one()
        langs = self.backend_id.lang_ids
        if langs:
            self.lang_id = langs[0]
            return {'domain': {'lang_id': [('id', 'in', langs.ids)]}}

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderProduct, self).default_get(fields_list)
        if 'backend_id' in fields_list:
            backend = self.env['locomotive.backend'].search([], limit=1)
            res['backend_id'] = backend.id
            if backend and backend.lang_ids and 'lang_id' in fields_list:
                res['lang_id'] = backend.lang_ids[0].id
        return res


class ShopinvaderVariant(models.Model):
    _name = 'shopinvader.variant'
    _inherits = {
        'shopinvader.product': 'shopinvader_product_id',
        'product.product': 'record_id'}

    shopinvader_product_id = fields.Many2one(
        'shopinvader.product',
        required=True,
        ondelete='cascade')
    record_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='cascade')

    # TODO some field are related to the template
    # stock_state
    # images
    # from price / best discount

    categories = fields.Many2many(
        comodel_name='shopinvader.category',
        compute='_compute_categories',
        string='Shopinvader Categories')

    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')
    variant_count = fields.Integer(
        related='product_variant_count')

    attributes = fields.Serialized(
        compute='_compute_attributes',
        string='Shopinvader Attributes'
    )

    def _get_categories(self):
        self.ensure_one()
        return self.categ_id

    @api.depends('categ_id.shopinvader_bind_ids')
    def _compute_categories(self):
        for record in self:
            shop_categs = []
            for categ in record._get_categories():
                for loco_categ in categ.shopinvader_bind_ids:
                    if loco_categ.backend_id == record.backend_id:
                        shop_categs.append(loco_categ.id)
                        break
            record.categories = shop_categs

    def _compute_image(self):
        for record in self:
            images = []
            for image in record.record_id.image_ids:
                res = {'original': image.url}
                for resize in record.backend_id.image_resize_ids:
                    res[resize.key] = \
                        image.get_thumbnail_from_resize(resize).url
                images.append(res)
            record.images = images

    def _compute_attributes(self):
        for record in self:
            attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                attributes[sanitized_key] = att_value.name
            record.attributes = attributes

    def _get_price(self, pricelist, fposition):
        self.ensure_one()
        return self._get_price_per_qty(1, pricelist, fposition)

    def _extract_price_from_onchange(self, pricelist, onchange_vals):
        tax_ids = onchange_vals['value']['tax_id']
        tax_included = False
        if tax_ids:
            # Becarefull we only take in account the first tax for
            # determinating if the price is tax included or tax excluded
            # This may not work in multi-tax case
            tax = self.env['account.tax'].browse(tax_ids[0])
            tax_included = tax.price_include
        prec = self.env['decimal.precision'].precision_get('Product')
        return {
            'value': round(onchange_vals['value']['price_unit'], prec),
            'tax_included': tax_included,
            }

    def _get_price_per_qty(self, qty, pricelist, fposition):
        # Get an partner in order to avoid the raise in the onchange
        # the partner selected will not impacted the result
        partner = self.env['res.partner'].search([], limit=1)
        result = self.env['sale.order.line'].product_id_change(
            pricelist.id, self.record_id.id, qty=qty,
            fiscal_position=fposition.id, partner_id=partner.id)
        return self._extract_price_from_onchange(pricelist, result)
