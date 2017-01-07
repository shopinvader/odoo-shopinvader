# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import StringIO
import base64
from openerp.addons.connector_locomotivecms.backend import locomotivecms
from openerp.addons.connector.unit.mapper import mapping, ExportMapChild
from openerp.addons.connector_generic.unit.mapper import GenericExportMapper
from slugify import slugify
from openerp.tools.image import image_resize_image


@locomotivecms
class ProductExportMapper(GenericExportMapper):
    _model_name = 'locomotivecms.product'

    direct = [
        ('name', 'name'),
        ('prefix_code', 'prefix_code'),
        ('url_key', 'url_key'),
        ('id', 'id'),
        ('description', 'description'),
        ('stock_state', 'stock_state'),
        ('qty_available', 'stock_qty'),
        ]

    children = [
        ('product_variant_ids', 'variants', 'product.product'),
        ]

    def _apply(self, map_record, options=None):
        res = super(ProductExportMapper, self)._apply(map_record, options=options)
        res.update({
            'from_price': 10, # en tenant compte des qty
            'discount_old_price': 15,
            'discount_value': 25,
            'brand': [],
            'technical_files': [],
            'brand': 'UStronic',
            })
        return {
            'categories': [
            '586bfd1f7aa7460007061945',
            '586bfd1f7aa7460007061948',
            ],
            'data': res,
            'name': res['prefix_code'],
            '_slug': res['url_key'],
            'odoo_id': str(res.pop('id')),
            }

    @mapping
    def image(self, record):
        binder = self.binder_for('locomotivecms.image')
        res = []
        for image in record.image_ids:
            image_data = {'name': image.name}
            for binding in image.locomotivecms_bind_ids:
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
        if not 'product_links' in self.env.registry._init_modules:
            return {}
        binder = self.binder_for('locomotivecms.product')

        def get_binding(record, link_type):
            res = []
            for link in record.product_link_ids:
                if link.type == link_type and link.is_active:
                    external_id = binder.to_backend(
                        link.linked_product_tmpl_id,
                        wrap=True)
                    res.append(external_id)
            return res

        return {
            'cross_sellings': get_binding(record, 'cross_sell'),
            'relateds': get_binding(record, 'related'),
            'up_sellings': get_binding(record, 'up_sell')
        }

@locomotivecms
class LocomotiveExportMapChild(ExportMapChild):
    _model_name = 'product.product'


@locomotivecms
class ProductProductMapper(GenericExportMapper):
    _model_name = 'product.product'

    direct = [
        ('face', 'face'),
        ('fuse', 'fuse'),
        ('color', 'color'),
        ('default_code', 'default_code'),
        ('stock_state', 'stock_state'),
        ('qty_available', 'stock_qty'),
    ]

    @mapping
    def image(self, record):
        binder = self.binder_for('locomotivecms.image')
        res = []
        for image in record.image_ids:
            image_data = {'name': image.name}
            for binding in image.locomotivecms_bind_ids:
                if binding.backend_id == self.backend_record:
                    image_data[binding.size] = binding.url
            res.append(image_data)
        return {'images': res}

    @mapping
    def name(self, record):
        return {'name': record.color}

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
    def technical(self, record):
        return {
            'technical_details': [
                {"name": "Poids net", "value": "0.0450"},
                {"name": "Marque", "value": "Adaptoo"},
                {"name": "Eco-part.", "value": "0.01"},
                {"name": "Info", "value": "Type G"},
                {"name": "Dimensions", "value": "L.6,0 x l.5,0 x h.5,0 cm"},
                {"name": "Etat", "value": "Direct Usine"},
        ]}

    @mapping
    def stock(self, record):
        return {
            'stock_state': 'in_stock',
            'stock_qty': 42,
        }


@locomotivecms
class ImageExportMapper(GenericExportMapper):
    _model_name = 'locomotivecms.image'

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
