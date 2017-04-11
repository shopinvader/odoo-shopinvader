# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import StringIO
import base64
from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.addons.connector.unit.mapper import mapping, ExportMapChild
from openerp.addons.connector_generic.unit.mapper import GenericExportMapper
from openerp.tools.image import image_resize_image

import logging

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug('Can not import slugify')


@locomotive
class CategExportMapper(GenericExportMapper):
    _model_name = 'locomotive.category'

    direct = [
        ('name', 'name'),
        ('seo_title', 'seo_title'),
        ('meta_description', 'meta_description'),
        ('meta_keyword', 'meta_keywords'),
        ('subtitle', 'subtitle'),
        ('link_label', 'link_label'),
        ('short_description', 'short_description'),
        ('description', 'description'),
        ('url_key', 'url_key'),
    ]

    def _apply(self, map_record, options=None):
        res = super(CategExportMapper, self)._apply(
            map_record, options=options)
        return {
            'seo_title':  res.pop('seo_title'),
            'meta_keywords': res.pop('meta_keywords'),
            'meta_description': res.pop('meta_description'),
            '_slug': res['url_key'],
            'erp_id': map_record._source.record_id.id,
            'name': res['name'],
            'data': res,
            'products': res.pop('products'),
            'link_label': res['link_label'],
            }

    @mapping
    def filter(self, record):
        data = []
        for filter in record.filter_ids:
            data.append({
                'name': filter.name,
                'attribute': filter.field_id.name,
                'help': filter.help,
                })
        return {'filter': data}

    @mapping
    def image(self, record):
        res = []
        for image in record.image_ids:
            image_data = {'name': image.name}
            for binding in image.locomotive_bind_ids:
                if binding.backend_id == self.backend_record:
                    image_data[binding.size] = binding.url
            res.append(image_data)
        return {'images': res}

    @mapping
    def products(self, record):
        binder = self.binder_for('locomotive.product')
        products = []
        domain = [('categ_id', '=', record.record_id.id)]
        if 'product_m2mcategories' in self.env.registry._init_modules:
            domain = ['|', ('categ_ids', '=', record.record_id.id)] + domain
        for product in self.env['product.template'].search(domain):
            external_id = binder.to_backend(product, wrap=True)
            if external_id:
                products.append(external_id)
        return {
            'products': products,
            }


@locomotive
class ProductExportMapper(GenericExportMapper):
    _model_name = 'locomotive.product'

    direct = [
        ('name', 'name'),
        ('prefix_code', 'prefix_code'),
        ('url_key', 'url_key'),
        ('description', 'description'),
        ('stock_state', 'stock_state'),
        ('qty_available', 'stock_qty'),
        ('seo_title', 'seo_title'),
        ('meta_keyword', 'meta_keywords'),
        ('meta_description', 'meta_description'),
        ]

    children = [
        ('product_variant_ids', 'variants', 'product.product'),
        ]

    def _apply(self, map_record, options=None):
        res = super(ProductExportMapper, self)._apply(
            map_record, options=options)
        return {
            'seo_title':  res.pop('seo_title'),
            'meta_keywords': res.pop('meta_keywords'),
            'meta_description': res.pop('meta_description'),
            'categories': res.pop('categories'),
            '_slug': res['url_key'],
            'erp_id': map_record._source.record_id.id,
            'name': res['prefix_code'],
            'data': res,
            }

    @mapping
    def categories(self, record):
        binder = self.binder_for('locomotive.category')
        categories = []
        categories_name = []
        categories_ids = []
        if 'product_m2mcategories' in self.env.registry._init_modules:
            categs = record.categ_ids + record.categ_id
        else:
            categs = record.categ_id
        for categ in categs:
            external_id = binder.to_backend(categ, wrap=True)
            if external_id:
                categories.append(external_id)
                categories_name.append(categ.name)
                categories_ids.append(categ.id)
        return {
            'categories': categories,
            'categories_ids': categories_ids,
            'categories_name': categories_name,
            }

    @mapping
    def image(self, record):
        res = []
        for image in record.image_ids:
            image_data = {'name': image.name}
            for binding in image.locomotive_bind_ids:
                if binding.backend_id == self.backend_record:
                    image_data[binding.size] = binding.url
            res.append(image_data)
        return {'images': res}

    # TODO FIXME
    @mapping
    def lang_to_fix(self, record):
        rec = record.with_context(lang='fr_FR')
        return {'description': rec.description, 'name': rec.name}

    @mapping
    def comment(self, record):
        return {
            'rating_value': 5,
            'rating_nbr': 42,
            "comments": [
                {"partner": "dupond",
                 "name": "Top Top",
                 "description": "Trop fort chez adaptoo, produit qui déchire",
                 'rating': 5},
                {"partner": "durant",
                 "name": "Parfait",
                 "description": "produit de très bonne qualité",
                 'rating': 5},
            ]}

    @mapping
    def product_relation(self, record):
        if 'product_links' not in self.env.registry._init_modules:
            return {}

        def get_related_product(record, link_type):
            res = []
            # We export the odoo id of the linked product that
            # should be exported to the backend
            for link in record.product_link_ids:
                if link.type == link_type and link.is_active:
                    for binding in link.linked_product_tmpl_id.\
                            locomotive_bind_ids:
                        if binding.backend_id == record.backend_id:
                            res.append(link.linked_product_tmpl_id.id)
            return res
        return {
            'cross_sellings': get_related_product(record, 'cross_sell'),
            'relateds': get_related_product(record, 'related'),
            'up_sellings': get_related_product(record, 'up_sell'),
            }


@locomotive
class LocomotiveExportMapChild(ExportMapChild):
    _model_name = 'product.product'


@locomotive
class VariantExportMapper(GenericExportMapper):
    _model_name = 'product.product'

    direct = [
        ('default_code', 'default_code'),
        ('stock_state', 'stock_state'),
        ('qty_available', 'stock_qty'),
        ('id', 'erp_id'),
    ]

    @mapping
    def image(self, record):
        res = []
        for image in record.image_ids:
            image_data = {'name': image.name}
            for binding in image.locomotive_bind_ids:
                if binding.backend_id == self.backend_record:
                    image_data[binding.size] = binding.url
            res.append(image_data)
        return {'images': res}

    def _get_pricelist_info(self, record, pricelist):
        res = record._get_pricelist_dict(
            pricelist.record_id, pricelist.tax_included)
        return {'values': res, 'tax_included': pricelist.tax_included}

    @mapping
    def pricelist(self, record):
        res = {}
        for pricelist in self.backend_record.pricelist_ids:
            res[pricelist.code] = self._get_pricelist_info(record, pricelist)
        return {'pricelist': res}

    @mapping
    def media(self, record):
        res = []
        for media in record.media_ids:
            for binding in media.locomotive_bind_ids:
                if binding.backend_id == self.backend_record:
                    res.append({
                        'name': media.name,
                        'url': binding.url,
                        'type': binding.media_type})
        return {'media': res}


@locomotive
class ImageExportMapper(GenericExportMapper):
    _model_name = 'locomotive.image'

    @mapping
    def image(self, record):
        # get a slugify filename
        new_size = record._image_size[record.size]['resize']
        name = slugify(record.filename[:-4])
        if new_size:
            image = image_resize_image(record.image_main, new_size)
            name += '-%sx%s' % new_size
        else:
            image = record.image_main
        name += record.filename[-4:]
        f = StringIO.StringIO()
        f.write(base64.b64decode(image))
        f.seek(0)
        return {
            'file': f,
            'filename': name,
            }


@locomotive
class MediaExportMapper(GenericExportMapper):
    _model_name = 'locomotive.media'

    @mapping
    def media(self, record):
        # get a slugify filename
        f = StringIO.StringIO()
        f.write(base64.b64decode(record.datas))
        f.seek(0)
        return {
            'file': f,
            'filename': record.datas_fname,
            }


@locomotive
class PartnerExportMapper(GenericExportMapper):
    _model_name = 'locomotive.partner'

    direct = [
        ('email', 'email'),
        ('name', 'name'),
    ]
