# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
import base64
import logging
_logger = logging.getLogger(__name__)


try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

try:
    import unicodecsv as csv
    from slugify import slugify
except (ImportError, IOError) as err:
    _logger.debug(err)


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'

    def _get_variant_domain(self, lang):
        return [
            ('backend_id', '=', self.id),
            ('lang_id', '=', lang.id),
            ('record_id.ean13', '!=', False),
            ]

    def _get_absolute_url(self, url):
        return "%s/%s" % (self.location, url)

    def _get_variant_price(self, variant):
        main_role = self.role_ids.filtered('default')
        res = variant._get_price(
            main_role.pricelist_id, main_role.fiscal_position_ids[0])
        return "%s %s" % (
            res['value'], main_role.pricelist_id.currency_id.name)

    def _prepare_for_google_shopping(self, variant):
        images = variant.record_id.image_ids
        res = {
            'id': variant.default_code,
            'title': variant.name,
            'description': variant.description[0:5000],
            'link': self._get_absolute_url(
                variant.url_key + '?ref=%s' % variant.default_code),
            'image_link': images[0].url,
            'additional_image_link': ','.join([
                image.url for image in images[1:]]),
            'price': self._get_variant_price(variant),
            'google_product_category': variant.google_categ_id.google_id,
            'brand': variant.product_brand_id.name,
            'gtin': variant.record_id.ean13,
            'condition': 'new',
            'shipping': ':::0',
        }
        if variant.record_id.qty_available > 0:
            res['availability'] = 'in stock'
        else:
            res['availability'] = 'out of stock'
        return res

    def _get_storage_backend_id(self):
        """Choose the correct backend.

        By default : it's the one configured as ir.config_parameter
        Overload this method if you need something more powerfull
        """
        return int(self.env['ir.config_parameter'].get_param(
            'google_shopping_flux.backend_id'))

    def _get_storage_path(self, lang):
        return slugify(
            "%s-%s-google-shopping-flux"
            % (self.name, lang.code.replace('_', '-'))) + '.txt'

    def _generate_google_shopping_file(self, data, lang):
        f = StringIO.StringIO()
        writer = csv.DictWriter(
            f, encoding='utf-8', delimiter='\t', fieldnames=data[0].keys())
        writer.writeheader()
        for line in data:
            writer.writerow(line)
        f.seek(0)
        datas = base64.b64encode(f.read())
        storage_path = self._get_storage_path(lang)
        storage = self.env['storage.backend'].browse(
            self._get_storage_backend_id())
        storage.store(storage_path, datas, is_public=True)

    @api.multi
    def export_google_shopping_product(self):
        for backend in self:
            for lang in backend.lang_ids:
                domain = self._get_variant_domain(lang)
                data = []
                variants = self.env['shopinvader.variant'].with_context(
                    lang=lang.code).search(domain)
                for variant in variants:
                    data.append(self._prepare_for_google_shopping(variant))
                if data:
                    self._generate_google_shopping_file(data, lang)

    @api.model
    def export_all_google_shopping(self, domain=None):
        if domain is None:
            domain = []
        self.search(domain).export_google_shopping_product()
