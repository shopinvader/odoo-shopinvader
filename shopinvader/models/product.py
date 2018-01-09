# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
except:
    _logger.debug('Cannot `import unidecode`.')


def sanitize_attr_name(attribute):
    key = attribute.name
    return unidecode(key.replace(' ', '_').lower())

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.product',
        'record_id',
        string='Shopinvader Binding')
    description = fields.Html(translate=True)

    @api.multi
    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            record.shopinvader_bind_ids.unlink()
        return super(ProductTemplate, self).unlink()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        variant = super(ProductProduct, self).create(vals)
        for binding in variant.shopinvader_bind_ids:
            binding._create_shopinvader_variant()
        return variant


class ProductFilter(models.Model):
    _name = 'product.filter'
    _description = 'Product Filter'
    _order = 'sequence,name'

    sequence = fields.Integer()
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
                pfilter.display_name =\
                    'attributes.%s' % sanitize_attr_name(pfilter.attribute_id)


class ShopinvaderProduct(models.Model):
    _name = 'shopinvader.product'
    _description = 'Shopinvader Product'
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
            if not self.env['shopinvader.variant'].search([
                    ('record_id', '=', variant.id),
                    ('shopinvader_product_id', '=', self.id),
                    ]):
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
    _description = 'Shopinvader Variant'
    _inherits = {
        'shopinvader.product': 'shopinvader_product_id',
        'product.product': 'record_id'}

    default_code = fields.Char(
        related='record_id.default_code',
        readonly=True)
    shopinvader_product_id = fields.Many2one(
        'shopinvader.product',
        required=True,
        ondelete='cascade')
    record_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='cascade')
    object_id = fields.Integer(
        compute='_compute_object_id',
        store=True)
    shopinvader_categ_ids = fields.Many2many(
        comodel_name='shopinvader.category',
        compute='_compute_shopinvader_category',
        string='Shopinvader Categories')
    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')
    variant_count = fields.Integer(
        related='product_variant_count')
    attributes = fields.Serialized(
        compute='_compute_attributes',
        string='Shopinvader Attributes')
    main = fields.Boolean(
        compute='_compute_main_product')
    redirect_url_key = fields.Serialized(
        compute='_compute_redirect_url_key',
        string='Redirect Url Keys')

    @api.depends('record_id')
    def _compute_object_id(self):
        for record in self:
            record.object_id = record.record_id.id

    def _compute_redirect_url_key(self):
        for record in self:
            res = []
            for url in record.redirect_url_key_ids:
                res.append(url.url_key)
            record.redirect_url_key = res

    def _get_categories(self):
        self.ensure_one()
        return self.categ_id

    def _compute_shopinvader_category(self):
        for record in self:
            ids = []
            categs = record._get_categories()
            for categ in categs:
                parents = self.env['shopinvader.category'].search([
                    ('parent_left', '<=', categ.parent_left),
                    ('parent_right', '>=', categ.parent_right),
                    ('backend_id', '=', record.backend_id.id),
                    ])
                ids += parents.ids
            record.shopinvader_categ_ids = ids

    def _compute_image(self):
        for record in self:
            pass
            # TODO MIGRATE shopinvader_storage_image
            # images = []
            # for image in record.record_id.image_ids:
            #     res = {'original': image.url}
            #     for resize in record.backend_id.product_image_resize_ids:
            #         res[resize.key] = \
            #             image.get_thumbnail_from_resize(resize).url
            #     images.append(res)
            # record.images = images

    def _compute_attributes(self):
        for record in self:
            attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                attributes[sanitized_key] = att_value.name
            record.attributes = attributes

    def _get_price(self, pricelist, fposition, company=None):
        self.ensure_one()
        return self._get_price_per_qty(1, pricelist, fposition, company)

    def _get_price_per_qty(self, qty, pricelist, fposition, company=None):
        product_id = self.record_id
        taxes = product_id.taxes_id.sudo().filtered(
            lambda r: not company or r.company_id == company)
        tax_id = fposition.map_tax(taxes, product_id) if fposition else taxes
        tax_id = tax_id and tax_id[0]
        product = product_id.with_context(
            quantity=qty,
            pricelist=pricelist.id,
            fiscal_position=fposition,
        )
        final_price, rule_id = pricelist.get_product_price_rule(
            product, qty or 1.0, None)
        tax_included = tax_id.price_include
        value = self.env['account.tax']._fix_tax_included_price_company(
            final_price, product.taxes_id, tax_id, company)
        return {
            'value': value,
            'tax_included': tax_included
        }

    def _compute_main_product(self):
        for record in self:
            if record.record_id \
                    == record.product_tmpl_id.product_variant_ids[0]:
                record.main = True
            else:
                record.main = False
