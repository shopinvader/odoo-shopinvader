# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


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
        ]

    children = [
        ('product_variant_ids', 'product_variant_ids', 'product.product'),
        ]

    def _apply(self, map_record, options=None):
        res = super(ProductExportMapper, self)._apply(map_record, options=options)
        res.update({
            'stock_state': 'En stock',
            'from_price': 10, # en tenant compte des qty
            'discount_old_price': 15,
            'thunbmail': 'http://...',
            'discount_value': 25,
            'cross_sell_ids': [],
            'related_ids': [],
            'up_selling_ids': [],
            })
        return {
            'is_discounted': True,
            'is_bestseller': True,
            'is_bestdiscount': True,
            'data': res,
            'name': res['prefix_code'],
            '_slug': res['url_key'],
            'odoo_id': str(res.pop('id')),
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
        return {'image_ids': res}

    # TODO pricelist

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
        return {
            'base64': image,
            'filename': name,
            }
